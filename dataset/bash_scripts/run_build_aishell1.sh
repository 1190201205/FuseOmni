# bash load_dataset/build_aishell1_train.sh /data/share/voice_model_project/datasets/AIShell-1 train
# bash load_dataset/build_aishell1_train.sh /data/share/voice_model_project/datasets/AIShell-1 dev

CONDA_PATH="/mnt/afs/00036/software/conda/bin/activate"
CONDA_ENV="reap_omni"
source ${CONDA_PATH} ${CONDA_ENV}

# cd /mnt/afs/share/voice_model_project

PROJ_PATH=/mnt/afs/00036/project_fuseomni/FuseOmni/data

cd ${PROJ_PATH}

python ${PROJ_PATH}/load_dataset/multi_dataset.py \
--config /mnt/afs/00036/project_fuseomni/FuseOmni/data/load_dataset/multi_dataset_config.yaml \
--output /mnt/afs/00036/project_fuseomni/FuseOmni/data/reap_v1.jsonl

