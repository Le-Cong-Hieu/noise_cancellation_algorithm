
from noise_cancellation.lib import *
from noise_cancellation.function_cancellation import *
from sklearn.cluster import DBSCAN
from skimage import measure
from model_linear.train_model_linear_simulation import *
matplotlib.use('Agg')

def clear():
    os.system(" cls ")
def check_crack(image_input):
    return len(measure.regionprops(label(image_input, connectivity=2)))

def single_crack(point_crack):
    clustering = DBSCAN(eps=5, min_samples=12).fit(point_crack)
    return np.unique(clustering.labels_)
################################################################
#algos =  ["Deepcrack","EHCNN","FCN","HRNBM0.3","HED","Unet"]
def calculate_SNR_noise_dataset(algos,path_model_folder_input,path_crack_txt,SNR_num,num_point_add):
    data_crack_simulation = pd.read_csv(path_crack_txt,
                    index_col=False,sep=",")
    data_crack_simulation = (np.array(data_crack_simulation))
    list_R2, list_MAE, list_RMSE,list_M2 = [], [], [], []
    for algo in algos:
        list_image=glob.glob('./data/data_crack/%s/GT/*.png'%algo)
        arg_RMSE,arg_R2,arg_MAE=[],[],[]
        for k,path_img in  enumerate(list_image):
            img_input = cv2.imread(path_img)
            skeleton = skeletonize(img_input,method='lee')
            skeleton = cv2.cvtColor(skeleton, cv2.COLOR_BGR2GRAY)
            # check one crack
            print(k)
            if check_crack(skeleton) >= 2:
                continue
            point_crack = np.argwhere(skeleton > 0)
            if np.size(point_crack) < 1:
                print('image emtpy')
                continue
            if len(single_crack(point_crack)) >= 2:
                continue
            crack_nor,crack_predict,max_RMSE, max_MAE, max_R2,name_model_best =find_model_best_crack(
                        data_crack_simulation,point_crack,path_model_folder_input,SNR_num,num_point_add)
            arg_RMSE.append(max_RMSE)
            arg_R2.append(max_R2)
            arg_MAE.append(max_MAE)
        list_RMSE.append(sum(arg_RMSE) / len(arg_RMSE))
        list_MAE.append(sum(arg_MAE) / len(arg_MAE))
        list_R2.append(sum(arg_R2) / len(arg_R2))
        list_M2.append(sum(arg_RMSE) / len(arg_RMSE)+sum(arg_MAE) / len(arg_MAE)+1-sum(arg_R2) / len(arg_R2))
    return list_R2, list_MAE, list_RMSE,list_M2   
def save_fig(df,name):
    #["Crack_500","Cracktree","CrackForest","CRKWH_100","CrackLS315"]
    SNR_num  = df.index
    Crack_500   = df ['Crack_500'].tolist()
    Cracktree   = df ['CrackTree260'].tolist()
    CrackForest = df ['CFD'].tolist()
    CRKWH_100   = df ['CRKWH100'].tolist()
    CrackLS315   = df ['CrackLS315'].tolist()
    #moisturizerSalesData = df ['moisturizer'].tolist()
    plt.plot(SNR_num, Crack_500,   label = 'Crack_500 Data', marker='o', linewidth=3)
    plt.plot(SNR_num, Cracktree,   label = 'Cracktree Data',  marker='o', linewidth=3)
    plt.plot(SNR_num, CrackForest, label = 'CrackForest Data', marker='o', linewidth=3)
    plt.plot(SNR_num, CRKWH_100, label = 'CRKWH_100 Data', marker='o', linewidth=3)
    plt.plot(SNR_num, CrackLS315, label = 'CrackLS315 Data', marker='o', linewidth=3)
    #plt.plot(monthList, moisturizerSalesData, label = 'ToothPaste Sales Data', marker='o', linewidth=3)
    plt.xlabel('SNR Number')
    #plt.ylabel('Sales units in number')
    plt.legend(loc='upper left')
    plt.xticks(SNR_num)
    #plt.yticks([1000, 2000, 4000, 6000, 8000, 10000, 12000, 15000, 18000])
    #plt.title('Sales data')
    #plt.show()
    path = './output/save_grap'
    if not os.path.exists(path):
            os.mkdir(path)
    path_save = path + name + '.png'
    plt.savefig(path_save)
    plt.figure().clear()
    plt.close()
    plt.close('all')
    plt.cla()
    plt.clf()
###############################
def find_SNR_best():
    MAE_data,RMSE_data, R2_data,M2_data,lst_SNR=[],[],[],[],[]
    #algos_data =  ["Crack_500"]#,"Cracktree","CrackForest","CRKWH_100","CrackLS315"]
    for SNR_num in range(10,90,5):
        algos_data =  ["CFD","Crack_500","CrackLS315","CrackTree260","CRKWH100"]
        list_class_model=[Linear_Model_LM,Gaussian_GPR,Tree,SVM] #,Gaussian_GPR,Tree,SVM
        show_fig= None
        path_crack_simulation='./data/Tex1000_1n_1cd__3p.txt'
        path_save ='./model_linear/model/'
        save_model_ML = True
        path_image_test ='D:/imgage_label/image_label.png'
        Snr_db=SNR_num
        num_point_add =10 
        train_model_linear(list_class_model,path_crack_simulation,path_save,show_fig,save_model_ML,path_image_test,Snr_db,num_point_add)
        path_crack_txt='./data/Tex1000_1n_1cd__3p.txt'
        path_model_folder_input= './model_linear/model/Tex1000_1n_1cd__3p'
        #SNR_num = 1
        #num_point_add =10
        list_R2, list_MAE, list_RMSE,list_M2=calculate_SNR_noise_dataset(algos_data,path_model_folder_input
                                                                ,path_crack_txt,SNR_num,num_point_add)
        MAE_data.append(list_MAE)
        RMSE_data.append(list_RMSE)
        R2_data.append(list_R2)
        M2_data.append(list_M2)
        lst_SNR.append(SNR_num)
    df_RMSE=pd.DataFrame(data=MAE_data, index=lst_SNR, columns=algos_data)    
    df_MAE=pd.DataFrame(data=RMSE_data,  index=lst_SNR,columns=algos_data)
    df_R2=pd.DataFrame(data=R2_data,  index=lst_SNR,columns=algos_data)
    df_M2=pd.DataFrame(data=M2_data, index=lst_SNR, columns=algos_data)
    df_M2['sum'] =  df_M2.sum(axis=1)
    SNR_best = df_M2.index[df_M2['sum'].idxmin()]
    save_fig(df_RMSE,'RMSE')
    save_fig(df_MAE,'MAE')
    save_fig(df_R2,'R2')
    save_fig(df_M2,'M2')
    return SNR_best

if __name__ == '__main__':
    SNR_best = find_SNR_best()