import easyocr
import glob , cv2 , os
reader = easyocr.Reader(['ch_sim', 'en'])
#=========== detection text=========================
def text_detection(img):
    imProcess = img.copy()
    results = reader.readtext(img)
    list_pos_text_area = []
    # iterate on all resultsif
    if results != []:
        for res in results:
            top_left = tuple(res[0][0])  # top left coordinates as tuple
            bottom_right = tuple(res[0][2])  # bottom right coordinates as tuple
            box = top_left+bottom_right # (x1,y1,x2,y2)
            list_pos_text_area.append(box)
    return list_pos_text_area
lis_paths_img = glob.glob(r'F:\Foxconn\CCD_Labels\data\Images\part1\OK\areaLB\*.jpg')
for pIm in lis_paths_img:
    img_name = os.path.basename(pIm).split('.')[0]
    img =cv2.imread(pIm)
    lis_pos_text_area = text_detection(img=img)
    path_save_text_area = fr'F:\Foxconn\CCD_Labels\data\Images\part1\OK\areaLB\text_area\{img_name}'
    if lis_pos_text_area:
        i=0
        for pos in lis_pos_text_area:
            # extract text area
            text_area = img[pos[1]:pos[3], pos[0]:pos[2]]
            os.makedirs(path_save_text_area , exist_ok=True)
            cv2.imwrite(path_save_text_area + f'\\{img_name}_text_area_{i}.jpg' , text_area)
            i+=1


