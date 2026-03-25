#!/bin/bash

# Configuration and positional arguments
# $1: CUDA_VISIBLE_DEVICES (e.g., "0,1,2,3,4,5,6,7")
# $2: pruning_method (e.g., "reap")
# $3: seed (default 42)
# $4: compression_ratio (default 0.5)

export CUDA_VISIBLE_DEVICES=${1:-"0,1,2,3,4,5,6,7"}
pruning_method=${2:-"reap"}
seed=${3:-42}
compression_ratio=${4:-0.5}

IFS=',' read -ra GPU_VAR <<< "${CUDA_VISIBLE_DEVICES}"
NUM_GPUS=${#GPU_VAR[@]}
NUM_SHARDS=$((NUM_GPUS / 2))

if [ "$NUM_SHARDS" -eq 0 ]; then
    NUM_SHARDS=1
fi

# Fixed parameters
model_name="/mnt/afs/share/Qwen3-Omni-30B-A3B-Instruct"
dataset_name="/mnt/afs/00036/project_fuseomni/FuseOmni/data/airshell1/aishell1_test_asr.jsonl"
num_samples=1024
output_file_name="observations_${num_samples}_cosine-seed_${seed}.pt"

# Path to Conda and environment
CONDA_PATH="/mnt/afs/00036/software/conda/bin/activate"
CONDA_ENV="reap_omni"
source ${CONDA_PATH} ${CONDA_ENV}

echo "Running Qwen3-Omni thinker pruning with dataset: $dataset_name"
cd /mnt/afs/00036/project_fuseomni/FuseOmni/reap

# --- Phase 1: Observation Shards ---
for i in $(seq 0 $((NUM_SHARDS-1))); do
    GPU1=${GPU_VAR[$((i * 2))]}
    GPU2=${GPU_VAR[$((i * 2 + 1))]}
    SHARD_CUDA="${GPU1},${GPU2}"
    if [ -z "$GPU2" ]; then
        SHARD_CUDA="${GPU1}"
    fi
    PORT=$((8000 + GPU1))
    
    echo "Starting observer for shard $i on GPUs $SHARD_CUDA"
    
    CUDA_VISIBLE_DEVICES=$SHARD_CUDA python src/reap/prune.py \
        --model_name "$model_name" \
        --dataset_name "$dataset_name" \
        --compression_ratio $compression_ratio \
        --prune_method $pruning_method \
        --profile false \
        --vllm_port $PORT \
        --server_log_file_name "pruning-cli-${GPU1}.log" \
        --do_eval false \
        --distance_measure cosine \
        --seed $seed \
        --output_file_name ${output_file_name} \
        --singleton_super_experts false \
        --singleton_outlier_experts false \
        --samples_per_category ${num_samples} \
        --record_pruning_metrics_only false \
        --num_shards $NUM_SHARDS \
        --shard_idx $i \
        --run_observer_only true &
done

echo "Waiting for all shards to finish observing..."
wait
echo "All shards finished. Running merge..."

# --- Phase 2: Merge Shards ---
MERGE_CUDA="${GPU_VAR[0]},${GPU_VAR[1]}"
if [ -z "${GPU_VAR[1]}" ]; then
    MERGE_CUDA="${GPU_VAR[0]}"
fi

CUDA_VISIBLE_DEVICES=$MERGE_CUDA python src/reap/prune.py \
    --model_name "$model_name" \
    --dataset_name "$dataset_name" \
    --compression_ratio $compression_ratio \
    --prune_method $pruning_method \
    --profile false \
    --vllm_port $((8000 + ${GPU_VAR[0]})) \
    --server_log_file_name "pruning-cli-${GPU_VAR[0]}.log" \
    --do_eval false \
    --distance_measure cosine \
    --seed $seed \
    --output_file_name ${output_file_name} \
    --singleton_super_experts false \
    --singleton_outlier_experts false \
    --samples_per_category ${num_samples} \
    --record_pruning_metrics_only false \
    --num_shards $NUM_SHARDS \
    --merge_shards true

echo "Pruning and merge completed."

# --- Phase 3: Cluster Analysis and Plotting ---
echo "Proceeding to cluster analysis and plotting..."

# Derive observation file path consistent with main.py create_results_directory
MODEL_BASE=$(basename "$model_name")
DATASET_BASE=$(basename "$dataset_name")
# results_dir = ./artifacts / model_clean / dataset_clean + str(num_samples)
# for model, they just use the last part after "/"
OBSERVATIONS_DIR="artifacts/${MODEL_BASE}/${DATASET_BASE}${num_samples}/all"
OBS_FILE="${OBSERVATIONS_DIR}/${output_file_name}"
OUTPUT_DIR="fig/qwen3-omni-clusters"

mkdir -p ${OUTPUT_DIR}

echo "Running cluster analysis for Qwen3-Omni..."
echo "Observations: ${OBS_FILE}"
echo "Output: ${OUTPUT_DIR}"

# Run the clustering and plotting
python src/reap/cluster.py \
    --observations_path "${OBS_FILE}" \
    --output_dir "${OUTPUT_DIR}" \
    --compression_ratio $compression_ratio \
    --expert_sim "router_logits" \
    --cluster_method "agglomerative" \
    --export_activations

echo "Plotting completed. Check ${OUTPUT_DIR} for results."
