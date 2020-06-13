import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import imageio
import joblib
from shutil import copy2, rmtree
from datetime import datetime, timedelta


def clean_nan(array):
    if type(array) == list:
        array = np.asarray(array) 
    not_nan_array = ~ np.isnan(array)
    return array[not_nan_array]

def join_list_names(names):
    join_names = ''
    for name in names:
        join_names += name+' and '
    return join_names[:-5]
    
def get_max_min(sufx, data_dir, max_min):
    if max_min == 'max':
        return max(set([ pd.to_datetime(f'2020-{date[-8:-6]}-{date[-6:-4]}',format = "%Y/%m/%d") for date in data_dir if date.startswith(sufx)]))
    if max_min == 'min':
        return min(set([ pd.to_datetime(f'2020-{date[-8:-6]}-{date[-6:-4]}',format = "%Y/%m/%d") for date in data_dir if date.startswith(sufx)]))

def get_max_day(state, newest_date):
    
    if type(state) == list:
        
        return max([max(newest_date[newest_date['nombre'] == local].values[0][3:]) for local in state])
    else:
        
        return max(newest_date[newest_date['nombre'] == state].values[0][3:])
    
def get_max_cummulative(state, newest_date):
    if type(state) == list:
        return max([sum(newest_date[newest_date['nombre'] == local].values[0][3:]) for local in state])
    else:
        return sum(newest_date[newest_date['nombre'] == state].values[0][3:])
    
def get_cummulative_record(plot_data):
    cummulative_record = []
    last_valid = int()
    for i in plot_data:

        if len(cummulative_record) == 0:
            if not np.isnan(i):
                cummulative_record.append(i)
                last_valid = i
            else:
                cummulative_record.append(np.nan)
                last_valid = 0
        else:
            if not np.isnan(i):
                cummulative_record.append(i+last_valid)
                last_valid += i

            else:
                cummulative_record.append(np.nan)
    return cummulative_record

def make_mp4(state,dtype,max_date):
    if type(state) == list:
        state = join_list_names(state)
    
    for _ in range(30):
        copy2(f'plots/{state}/cummulative/{dtype}/{max_date}.jpg', f'plots/{state}/cummulative/{dtype}/{max_date}_{_}.jpg')
        copy2(f'plots/{state}/discrete/{dtype}/{max_date}.jpg', f'plots/{state}/discrete/{dtype}/{max_date}_{_}.jpg')

    if not os.path.exists(f'results/{state}'):
        os.makedirs(f'results/{state}')

    cum_images = []

    for filename in os.listdir(f'plots/{state}/cummulative/{dtype}'):
        cum_images.append(imageio.imread(os.path.join(f'plots/{state}/cummulative/{dtype}',filename)))
    imageio.mimsave(f'results/{state}/{dtype}_cummulative_{state}.mp4', cum_images)

    dis_images = []

    for filename in os.listdir(f'plots/{state}/discrete/{dtype}'):
        dis_images.append(imageio.imread(os.path.join(f'plots/{state}/discrete/{dtype}',filename)))
    imageio.mimsave(f'results/{state}/{dtype}_discrete_{state}.mp4', dis_images)
    
    rmtree('plots')

def make_plots(index, plot_index, state, file, dtype, max_day, max_cummulative,trim):
    
    if not os.path.exists(f'plots/{state}/cummulative/{dtype}'):
        os.makedirs(f'plots/{state}/cummulative/{dtype}')
        
    if not os.path.exists(f'plots/{state}/discrete/{dtype}'):
        os.makedirs(f'plots/{state}/discrete/{dtype}')
        
    data = pd.read_csv(os.path.join(data_path,file))
    data = data[data['nombre'] == state]
    dates = pd.to_datetime(data.columns[3:], dayfirst=True)
    
    plot_data = []
                       
    for day in index:
        try:
            plot_data.append(data[str(day)[-11:-9]+str(day)[-15:-11]+str(day)[:4]].values[0])
        except:
            plot_data.append(np.nan)
    
    plot_single_discrete(index, plot_index, plot_data, state, file, dtype, max_day,trim)
    
    plot_single_cummulative(index, plot_index, plot_data, state, file, dtype, max_cummulative,trim)    
    
    print(f'Plots of {dtype} ready for day: {calendar.month_name[int(file[-8:-6])]} {file[-6:-4]}')

def make_multi_plots(index, plot_index, state, days, sufx_items, max_day, max_cummulative,trim,dtypes):
    
    if not os.path.exists(f'plots/{state}/cummulative/{dtypes}'):
        os.makedirs(f'plots/{state}/cummulative/{dtypes}')
        
    if not os.path.exists(f'plots/{state}/discrete/{dtypes}'):
        os.makedirs(f'plots/{state}/discrete/{dtypes}')
    
    data = [pd.read_csv(os.path.join(data_path,x)) for x in days]
    data = [x[x['nombre'] == state] for x in data]
        
    plot_data = {key:[] for key in sufx_items.keys()}
    
    
    
    for ind, key in enumerate(plot_data.keys()):
        for day in index:
            try:
                plot_data[key].append(data[ind][str(day)[-11:-9]+str(day)[-15:-11]+str(day)[:4]].values[0])
            except:
                plot_data[key].append(np.nan)
    
    plot_multi_discrete(index, plot_index, plot_data, days, dtypes, state, max_day,trim)
    plot_multi_cummulative(index, plot_index, plot_data, days, dtypes, state, max_cummulative,trim)
    print(f'Plots of {dtypes} ready for day: {calendar.month_name[int(days[0][-8:-6])]} {days[0][-6:-4]}')

def get_indexes(sufx, data_dir, state):

    newest_date = max(set([ pd.to_datetime(f'2020-{date[-8:-6]}-{date[-6:-4]}',format = "%Y/%m/%d") for date in data_dir if date.startswith(sufx)]))
    oldest_date = min(set([ pd.to_datetime(f'2020-{date[-8:-6]}-{date[-6:-4]}',format = "%Y/%m/%d") for date in data_dir if date.startswith(sufx)]))

    newest_date = pd.read_csv(os.path.join( data_path, sufx + str(newest_date)[-14:-12]+str(newest_date)[-11:-9]+'.csv') )
    oldest_date = pd.read_csv(os.path.join( data_path, sufx + str(oldest_date)[-14:-12]+str(oldest_date)[-11:-9]+'.csv') )

    max_day = max(newest_date[newest_date['nombre'] == state].values[0][3:])
    max_cummulative = sum(newest_date[newest_date['nombre'] == state].values[0][3:])
    
    index = pd.date_range(start= pd.to_datetime(oldest_date.columns[3], dayfirst=True), end = pd.to_datetime(newest_date.columns[-1], dayfirst=True))
    plot_index = [calendar.month_name[int(str(x)[5:-12])] + ' / ' + str(x)[8:-9]  for x in index]
        
    return index, plot_index, max_day, max_cummulative

def get_multi_indexes(files, data_dir, state, sufx_items):
    
    newest_date = max(set([ pd.to_datetime(f'2020-{date[-8:-6]}-{date[-6:-4]}',format = "%Y/%m/%d") for date in files[list(sufx_items.keys())[0]]]))
    oldest_date = min(set([ pd.to_datetime(f'2020-{date[-8:-6]}-{date[-6:-4]}',format = "%Y/%m/%d") for date in files[list(sufx_items.keys())[0]]]))
    
    longest_data_check = 0
    longest_data = ''
    max_day = 0
    max_cummulative = 0
    
    for dtype in files.keys():
        
        data_check = pd.read_csv(os.path.join( data_path, sufx_items[dtype] + str(newest_date)[-14:-12]+str(newest_date)[-11:-9]+'.csv'))
        max_discrete = max(data_check[data_check['nombre'] == state].values[0][3:])
        sum_cummulative = sum(data_check[data_check['nombre'] == state].values[0][3:])
        
        if len(data_check.columns[3:]) > longest_data_check:
            longest_data_check == len(data_check.columns[3:])
            longest_data = data_check[data_check['nombre'] == state]
            
        if  max_discrete > max_day:
            max_day = max_discrete
        if sum_cummulative > max_cummulative:
            max_cummulative = sum_cummulative
    
    index = pd.date_range(start= pd.to_datetime(longest_data.columns[3], dayfirst=True), end = pd.to_datetime(longest_data.columns[-1], dayfirst=True))
    plot_index = [calendar.month_name[int(str(x)[5:-12])] + ' / ' + str(x)[8:-9]  for x in index]
    
    return index, plot_index, max_day, max_cummulative

