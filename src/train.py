import sys, json
import torch
import os
import numpy as np
import opennre
from opennre import encoder, model, framework
import argparse

root_path = '../data/'

parser = argparse.ArgumentParser()
parser.add_argument('--mask_entity', action='store_true', help='Mask entity mentions')
args = parser.parse_args()

sys.path.append(root_path)
if not os.path.exists('ckpt'):
    os.mkdir('ckpt')
ckpt = 'ckpt/wiki80_bert_softmax.pth.tar'

# load relation to id dictionary
rel2id = json.load(open(os.path.join(root_path, 'dataset/wiki80/wiki80_rel2id.json')))

# Create BERT encoder
sentence_encoder = opennre.encoder.BERTEncoder(
    max_length=80, 
    pretrain_path=os.path.join(root_path, 'pretrain/bert-base-uncased'),
    mask_entity=args.mask_entity
)

# NN model
model = opennre.model.SoftmaxNN(sentence_encoder, len(rel2id), rel2id)

# Training framework
framework = opennre.framework.SentenceRE(
    train_path=os.path.join(root_path, 'dataset/wiki80/wiki80_train.txt'),
    val_path=os.path.join(root_path, 'dataset/wiki80/wiki80_val.txt'),
    test_path=os.path.join(root_path, 'dataset/wiki80/wiki80_val.txt'),
    model=model,
    ckpt=ckpt,
    batch_size=64, # Modify the batch size w.r.t. your device
    max_epoch=10,
    lr=2e-5,
    opt='adamw'
)

# Train model
framework.train_model()

# Test model
framework.load_state_dict(torch.load(ckpt)['state_dict'])
result = framework.eval_model(framework.test_loader)

# Evaluate model results
print('Accuracy on test set: {}'.format(result['acc']))
