#!/bin/bash

export CUDA_VISIBLE_DEVICES=${1:-"0,1,2,3,4,5,6,7"}
IFS=',' read -ra GPU_VAR <<< "${CUDA_VISIBLE_DEVICES}"
NUM_GPUS=${#GPU_VAR[@]}
NUM_SHARDS=$((NUM_GPUS / 2))

if [ "$NUM_SHARDS" -eq 0 ]; then
    NUM_SHARDS=1
fi

model_name="/mnt/afs/share/Qwen3-Omni-30B-A3B-Instruct"
dataset_name="/mnt/afs/00036/project_fuseomni/FuseOmni/data/airshell1/aishell1_test_asr.jsonl"
pruning_method=${2:-"reap"}
seed=${3:-42}
compression_ratio=${4:-0.5}

CONDA_PATH="/mnt/afs/00036/software/conda/bin/activate"
CONDA_ENV="reap_omni"
source ${CONDA_PATH} ${CONDA_ENV}

#num_samples=2048
num_samples=1024
output_file_name="observations_${num_samples}_cosine-seed_${seed}.pt"


echo "Running Qwen3-Omni thinker pruning with dataset: $dataset_name"
#    --results_dir /mnt/afs/00036/project_fuseomni/FuseOmni/reap/outputs \

cd /mnt/afs/00036/project_fuseomni/FuseOmni/reap

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
echo "All shards finished. Running merge and pruning..."

# Now run merge_shards and pruning
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
