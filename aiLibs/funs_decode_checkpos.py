import cv2
import numpy as np
import zxingcpp  # pip install zxing-cpp

''' ======================================= Step 1 : Decode ===================================='''


def decode_barcode_zxingcpp(img, fdraw=False):
    imProcess = img.copy()
    dict_Results = []
    # list_codes = []
    results = zxingcpp.read_barcodes(imProcess)
    for result in results:
        # list_codes.append(result.text)
        print("Found barcode:\n Text:    '{}'\n Format:   {}\n cfgPosition: {}".format(result.text, result.format, result.position))
        position = result.position
        x1 = (int(str(position).split(' ')[0].split('x')[0]), int(str(position).split(' ')[0].split('x')[1]))
        x2 = (int(str(position).split(' ')[1].split('x')[0]), int(str(position).split(' ')[1].split('x')[1]))
        x3 = (int(str(position).split(' ')[2].split('x')[0]), int(str(position).split(' ')[2].split('x')[1]))
        x4 = (int(str(position).split(' ')[3].split('x')[0]), int(str(position).split(' ')[3].split('x')[1].split('\x00')[0]))
        box = np.array([x1, x2, x3, x4])
        if fdraw:
            cv2.drawContours(imProcess, [box], 0, (0, 255, 0), 2)
            cv2.putText(imProcess, result.text, x1, cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
        dict_Results.append([result.text, box])
    # dict_Results['imProcess'] = imProcess
    # dict_Results['list_codes'] = list_codes
    if len(results) == 0:
        print("Could not find any barcode.")
    return dict_Results


def fnstep_check_can_read_ScanCode(im_Image1, im_Image2):
    h, w, _ = im_Image2.shape
    results_decode_Image1 = decode_barcode_zxingcpp(img=im_Image1)
    results_decode_Image2 = decode_barcode_zxingcpp(img=im_Image2)
    n3Code1 = len(results_decode_Image1)
    n3Code2 = len(results_decode_Image2)
    # cv2.putText(results_decode_Image2['imProcess'], f'Step 1 : Check barcode : {status}', (int(w / 2), int(h / 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    results_step1 = {
        'status': "OK" if n3Code1 == n3Code2 else "NG",
        'mess': f"[{n3Code1}, {n3Code2}]: Number of scancode [image1, image2] ",
        'results_decode_Image1': results_decode_Image1,
        'results_decode_Image2': results_decode_Image2
    }
    return results_step1


''' ======================================= Step 2 : Check Pos ===================================='''


# Loai bo duong vien xung quanh anh neu co
def convert_to_thresh(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 4)
    return thresh


def remove_boder_line_inThresh(thresh, disPixel):
    h, w = thresh.shape
    for i in range(w):
        for j in range(h):
            vl_pixel = thresh[j, i]
            if vl_pixel == 255:
                if j <= disPixel or i <= disPixel:
                    thresh[j, i] = 0
    return thresh


# Tim cac diem ngoai cung trong anh
def find_pos_most(thresh, debug=False):
    # Tìm tọa độ các pixel có giá trị 255
    coordinates = np.where(thresh == 255)
    coordinates = list(zip(coordinates[1], coordinates[0]))  # Hoán đổi x và y
    # Tìm pixel có tọa độ gần với bên trái, bên phải, bên trên và bên dưới nhất
    leftmost_pixel = min(coordinates, key=lambda p: p[0])
    rightmost_pixel = max(coordinates, key=lambda p: p[0])
    topmost_pixel = min(coordinates, key=lambda p: p[1])
    bottommost_pixel = max(coordinates, key=lambda p: p[1])
    # In ra tọa độ các pixel gần với bên trái, bên phải, bên trên và bên dưới nhất
    if debug:
        print("Leftmost Pixel  :", leftmost_pixel)
        print("Rightmost Pixel :", rightmost_pixel)
        print("Topmost Pixel   :", topmost_pixel)
        print("Bottommost Pixel:", bottommost_pixel)
    # crop
    thresh_boder = thresh[topmost_pixel[1]:rightmost_pixel[1], leftmost_pixel[0]:bottommost_pixel[0]]
    return thresh_boder, (leftmost_pixel, rightmost_pixel, topmost_pixel, bottommost_pixel)


def CompareDistancePASS(dist1, dist2, phantram_saiso=10):
    tb = (dist1 + dist2) / 2
    tb10phantram = tb / phantram_saiso
    hieu = abs(dist1 - dist2)
    return True if (hieu <= tb10phantram) else False


# Kiem tra lech vi
def fnstep_checkPos(im_Image2, threshold_percent, debug=False):
    imProcess = im_Image2.copy()
    h, w = imProcess.shape[:2]
    thresh = convert_to_thresh(image=imProcess)
    thresh = remove_boder_line_inThresh(thresh=thresh, disPixel=10)
    thresh_boder, tupPoint = find_pos_most(thresh)
    distance_left = tupPoint[0][0]
    distance_right = w - tupPoint[1][0]
    distance_top = tupPoint[2][1]
    distance_bot = h - tupPoint[3][1]

    LR_DistancePASS = CompareDistancePASS(distance_left, distance_right, threshold_percent)
    TB_DistancePASS = CompareDistancePASS(distance_top, distance_bot, threshold_percent)
    if LR_DistancePASS and TB_DistancePASS:
        status = "OK"
    else:
        status = "NG"
    if debug:
        sResult_pos = f'Khoang cach :\nleft:{distance_left}\nright:{distance_right}\ntop:{distance_top}\nbot:{distance_bot}\n'
        print(sResult_pos)
        cv2.line(imProcess, (0, tupPoint[0][1]), (tupPoint[0][0], tupPoint[0][1]), (0, 255, 0), 3)
        cv2.line(imProcess, (w, tupPoint[1][1]), (tupPoint[1][0], tupPoint[1][1]), (0, 255, 0), 3)
        cv2.line(imProcess, (tupPoint[2][0], 0), (tupPoint[2][0], tupPoint[2][1]), (0, 255, 0), 3)
        cv2.line(imProcess, (tupPoint[3][0], h), (tupPoint[3][0], tupPoint[3][1]), (0, 255, 0), 3)
        cv2.putText(imProcess, f'Step 2 : Check cfgPosition : {status}', (int(w / 2), int(h / 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    dict_results_step2 = {
        'status': status,
        'Lech_trai_phai': not LR_DistancePASS,  # Để vẽ khung, hoặc thông báo
        'Lech_tren_duoi': not TB_DistancePASS,
        'toado': [w, h, tupPoint]
    }
    return dict_results_step2


if __name__ == "__main__":
    label_area_Image1 = cv2.imread(r"F:\Foxconn\CCD_Labels\data\Images\part4\OK\OK1\areaLB\img_labels_NG_P4363_0.jpg")
    label_area_Image2 = cv2.imread(r"F:\Foxconn\CCD_Labels\data\Images\part4\NG\NG8_lech_vi\areaLB\img_labels_NG_P4558_0.jpg")
    dict_results_decode = fnstep_check_can_read_ScanCode(im_Image1=label_area_Image1, im_Image2=label_area_Image2)
    cv2.imshow('Decode Image1 ', dict_results_decode['imDecode_Image1_draw'])
    cv2.imshow('Decode Image2 ', dict_results_decode['imDecode_Image2_draw'])
    cv2.waitKey(0)
    dict_results_checkpos = fnstep_checkPos(im_Image2=label_area_Image2, threshold_percent=20)
    cv2.imshow('imProcess', dict_results_checkpos['imProcess'])
    cv2.waitKey(0)
