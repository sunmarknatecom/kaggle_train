import numpy as np
import glob
from pydicom import dcmread
from csv import writer
from tqdm import tqdm
from skimage.measure import compare_ssim as ssim

class PET_PT:
    def __init__(self, FINA=None):
        # file_name          =    FINA
        self.FINA = FINA

    def CONVERTING_FACTOR(self):

        DATA_SET = dcmread(self.FINA)

        # file_name          =    FINA
        # body_weight        =    BDWT
        # tracer_activity    =    TRAC
        # series_time        =    SETI
        # measure_time       =    METI
        # half_life          =    HALI
        # rescale_slope      =    RESL

        BDWT = DATA_SET[0x0010,0x1030].value
        TRAC = DATA_SET[0x0054,0x0016][0][0x0018,0x1074].value
        SETI = DATA_SET[0x0008,0x0032].value
        METI = DATA_SET[0x0054,0x0016][0][0x0018,0x1072].value
        HALI = DATA_SET[0x0054,0x0016][0][0x0018,0x1075].value
        RESL = DATA_SET[0x0028,0x1053].value

        # 4th step: arrangement of variables

        ST = SETI[0:6]
        MT = METI[0:6]
        RS = float(RESL)

        # hour_sec      = HS (시간을 초로 변환하기 위하여 3600 곱)
        # minute_sec    = MS (분을 초로 변환하기 위하여 60 곱)
        # second        = SE
        # total_time    = TT (unit: seconds)

        HS = (int(ST[0:2]) - int(MT[0:2])) * 3600
        MS = (int(ST[2:4]) - int(MT[2:4])) * 60
        SE = (int(ST[4:]) - int(MT[4:]))
        TT = HS + MS + SE

        # EXPO = exponential
        # ACAC = actual_activity

        EXPO = TT / HALI
        ACAC = TRAC * 2 ** (-1 * EXPO)

        # conversion_factor = cf

        CF= RS * BDWT * 1000 / ACAC

        return CF

    # def BASIC_STAT(self):
    #     INIT_CHR = input("STEP 1/5. TYPE THE NAME OF FILE >>>")
    #     START_NO = input("TYPE THE START NUMBER >>>")
    #     STOP_NUM = input("TYPE THE STOP NUMBER >>>")
    #     EXT_CHAR = "dcm"
    #     OUT_FILE = input("TYPE THE NAME OF OUPUT FILE >>>")
    #     INIT_LABEL = ['FILENAMES', 'SLICE NO', 'CF', 'BMI', 'MIN', 'MAX', 'MEAN', 'STD', 'VAR']

    #     f = open(OUT_FILE, 'w', newline='')
    #     wr = writer(f)
    #     wr.writerow(INIT_LABEL)

    #     pbar = tqdm(range(START_NO, STOP_NUM))

    #     for i in pbar:
    #         pbar.set_description("EXPORTING : ")
    #         fns = "%s%03d.%s" %(INIT_CHR, i, EXT_CHAR)
    #         ds_name = dcmread(fns)
    #         LIST = ds_name.pixel_array

    #         self.filename = ds_name[0x0010,0x1030].value
    #         self.tracer_activity = ds_name[0x0054,0x0016][0][0x0018,0x1074].value
    #         self.series_time = ds_name[0x0008,0x0032].value
    #         self.measure_time = ds_name[0x0054,0x0016][0][0x0018,0x1072].value
    #         self.half_life = ds_name[0x0054,0x0016][0][0x0018,0x1075].value
    #         self.rescale_slope = ds_name[0x0028,0x1053].value

    #         ST = self.tracer_activity[0:6]
    #         MT = self.measure_time[0:6]
    #         RS = float(self.rescale_slope)

    #         HS = (int(ST[0:2]) - int(MT[0:2])) * 3600
    #         MS = (int(ST[2:4]) - int(MT[2:4])) * 60
    #         SE = (int(ST[4:]) - int(MT[4:]))
    #         TT = HS + MS + SE

    #         EXPO = TT / self.half_life

    #         ACAC = self.tracer_activity * 2 **(-1 * EXPO)

    #         CF = RS * self.body_weight * 1000 / ACAC

    #         LIST_CF = LIST * CF

    #         self.height = ds_name[0x0010,0x1020].value
    #         BMI = self.body_weight / (self.height * self.height)
    #         SLICE_NO = ds_name[0x0020,0x1041].value
    #         CONV_DATA_LIST = [fns, SLICE_NO, CF, BMI, np.min(LIST_CF), np.max(LIST_CF), np.mean(LIST_CF), np.std(LIST_CF), np.var(LIST_CF)]
    #         wr.writerow(CONV_DATA_LIST)
    #     f.close()


    def BASIC_STAT_SERIAL(self, fn, output, list_names):
        
        time_value = str(fn)
        output_filename = str(output)

        initial_list = str(list_names).split()

        # initial_list = ["CJY", "CMS", "CSB", "HSL", "KBL", "KHY", "KJH", "KSO", "KYB", "KYC", "LJS", "LMD", "LYS", "LYT", "NSW", "PKC", "PMJ", "PSY", "PYH", "RJK", "YHS"] # GE
        # initial_list = ["AES", "CJH", "CJY", "HDO", "JCS", "JSY", "KHY", "KJW", "KJY", "KMY", "LBS", "LCJ", "LKY", "LSD", "NYJ", "PYS", "SUJ", "SYS", "WJS", "YKD", "YYH"] # SIEMENS
        # CJY CMS CSB HSL KBL KHY KJH KSO KYB KYC LJS LMD LYS LYT NSW PKC PMJ PSY PYH RJK YHS
        # AES CJH CJY HDO JCS JSY KHY KJW KJY KMY LBS LCJ LKY LSD NYJ PYS SUJ SYS WJS YKD YYH
        
        file_header = ["subject","image", "filenames", "Slice Number", "cf", "BMI", "min", "max", "mean", "std", "var"]

        f = open(output_filename, 'w', newline='')
        wr = writer(f)
        wr.writerow(file_header)

        for k, i in enumerate(initial_list):

            files_1 = '%s_%s_*.dcm' %(i,time_value)
            file_list_1 = sorted(glob.glob(files_1))
            file_number_1 = len(file_list_1)

            for j in range(file_number_1):
                fns = '%s_%s_%04d.dcm' %(i,time_value,j+1)
                print(fns)

                ds_name = dcmread(fns)

                bdwt = ds_name[0x0010,0x1030].value
                trac = ds_name[0x0054,0x0016][0][0x0018,0x1074].value
                seti = ds_name[0x0008,0x0032].value
                meti = ds_name[0x0054,0x0016][0][0x0018,0x1072].value
                half = ds_name[0x0054,0x0016][0][0x0018,0x1075].value
                resl = ds_name[0x0028,0x1053].value

                st = seti[0:6]
                mt = meti[0:6]
                rs = float(resl)

                hs = (int(st[0:2]) - int(mt[0:2])) * 3600
                ms = (int(st[2:4]) - int(mt[2:4])) * 60
                se = (int(st[4:]) - int(mt[4:]))
                tt = hs + ms + se

                expo = tt / half
                acac = trac * 2 ** (-1 * expo)

                cf= rs * bdwt * 1000 / acac

                list = ds_name.pixel_array                
                converted_list = list * cf

                height = ds_name[0x0010,0x1020].value
                BMI = bdwt / (height * height)
                slice_no = ds_name[0x0020,0x1041].value

                converted_data_first_order = [k+1,j+1, fns, slice_no, cf, BMI, np.min(converted_list), np.max(converted_list), np.mean(converted_list), np.std(converted_list), np.var(converted_list)]

                wr.writerow(converted_data_first_order)
                
        f.close()

def main():
    filename = input("Type filename: ")
    pt1 = PET_PT(FINA =filename)
    result = pt1.CONVERTING_FACTOR()
    return result

if "__init__" == "__main__":
    main()