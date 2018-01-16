#This script performs the linear color transfer step that 
#leongatys/NeuralImageSynthesis' Scale Control code performs.
#https://github.com/leongatys/NeuralImageSynthesis/blob/master/ExampleNotebooks/ScaleControl.ipynb
#Standalone script by github.com/htoyryla, and github.com/ProGamerGov

import numpy as np
import argparse
import scipy.ndimage as spi
from skimage import io,transform,img_as_float
from skimage.io import imread,imsave
from numpy import eye 

def match_color(target_img, source_img, output_name='output.png', mode='pca', eps=1e-5):
	'''
	Matches the colour distribution of the target image to that of the source image
	using a linear transform.
	Images are expected to be of form (w,h,c) and float in [0,1].
	Modes are chol, pca or sym for different choices of basis.
	'''
	target_img = spi.imread(target_img, mode="RGB").astype(float)/256
	source_img = spi.imread(source_img, mode="RGB").astype(float)/256
	
	mu_t = target_img.mean(0).mean(0)
	t = target_img - mu_t
	t = t.transpose(2,0,1).reshape(3,-1)
	Ct = t.dot(t.T) / t.shape[1] + eps * eye(t.shape[0])
	mu_s = source_img.mean(0).mean(0)
	s = source_img - mu_s
	s = s.transpose(2,0,1).reshape(3,-1)
	Cs = s.dot(s.T) / s.shape[1] + eps * eye(s.shape[0])
	if mode == 'chol':
		chol_t = np.linalg.cholesky(Ct)
		chol_s = np.linalg.cholesky(Cs)
		ts = chol_s.dot(np.linalg.inv(chol_t)).dot(t)
	if mode == 'pca':
		eva_t, eve_t = np.linalg.eigh(Ct)
		Qt = eve_t.dot(np.sqrt(np.diag(eva_t))).dot(eve_t.T)
		eva_s, eve_s = np.linalg.eigh(Cs)
		Qs = eve_s.dot(np.sqrt(np.diag(eva_s))).dot(eve_s.T)
		ts = Qs.dot(np.linalg.inv(Qt)).dot(t)
	if mode == 'sym':
		eva_t, eve_t = np.linalg.eigh(Ct)
		Qt = eve_t.dot(np.sqrt(np.diag(eva_t))).dot(eve_t.T)
		Qt_Cs_Qt = Qt.dot(Cs).dot(Qt)
		eva_QtCsQt, eve_QtCsQt = np.linalg.eigh(Qt_Cs_Qt)
		QtCsQt = eve_QtCsQt.dot(np.sqrt(np.diag(eva_QtCsQt))).dot(eve_QtCsQt.T)
		ts = np.linalg.inv(Qt).dot(QtCsQt).dot(np.linalg.inv(Qt)).dot(t)
	matched_img = ts.reshape(*target_img.transpose(2,0,1).shape).transpose(1,2,0)
	matched_img += mu_s
	matched_img[matched_img>1] = 1
	matched_img[matched_img<0] = 0
	imsave(output_name, matched_img)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--target', type=str, help="The image you are transfering color to. Ex: target.png", required=True)
	parser.add_argument('--source', type=str, help="The image you are transfering color from. Ex: source.png", required=True)
	parser.add_argument('--output', type=str, help="The name of your output image. Ex: output.png", default='output.png')
	parser.add_argument('--mode', type=str, help="The color transfer mode. Options are pca, chol, or sym.", default='pca')
	parser.add_argument('--eps', type=str, help="Your eps value in scientific notation or normal notation. Ex: 1e-5 or 0.00001", default=1e-5)
	parser.parse_args()
	args = parser.parse_args()
	target_img = args.target
	source_img = args.source
	output_name = args.output
	transfer_mode = args.mode
	eps_value = args.eps
	match_color(target_img, source_img, output_name, mode=transfer_mode, eps=float(eps_value))
