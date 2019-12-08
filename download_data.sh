data_folder=inverse_cooking_model/data
mkdir -p $data_folder

# These are the files URLs
ingr_VOCAB_URL=https://dl.fbaipublicfiles.com/inversecooking/ingr_vocab.pkl
instr_VOCAB_URL=https://dl.fbaipublicfiles.com/inversecooking/instr_vocab.pkl
model_URL=https://dl.fbaipublicfiles.com/inversecooking/modelbest.ckpt

# These are the file paths
ingr_VOCAB_FILE=./$data_folder/ingr_vocab.pkl
instr_VOCAB_FILE=./$data_folder/instr_vocab.pkl
model_FILE=./$data_folder/modelbest.ckpt

# Now DOWNLOAD!!
wget $instr_VOCAB_URL -O $instr_VOCAB_FILE
wget $ingr_VOCAB_URL -O $ingr_VOCAB_FILE
wget $model_URL -O $model_FILE
