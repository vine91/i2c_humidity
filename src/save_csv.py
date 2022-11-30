"""
 *  NOTE      - save_csv.py
 *  Author    - Ista
 *
 *  Created   - 2022.11.28
 *  Github    - https://github.com/vine91
 *  Contact   - vine9151@gmail.com
"""

import os, time, datetime
from _thread import *


class SaveCsv:
  """ Class of saving csv for SHT31. """

  def __init__(self):
    self.is_started = False
    self.present_time = ''

  def start(self):
    """ Function to Start """

    self.check_directory()
    self.is_started = True
    start_new_thread(self.start_date_thread, ())

  def start_date_thread(self):
    """ Function to Start Date Thread """

    while self.is_started:
      hour = datetime.datetime.now().strftime('%H')
      minute = datetime.datetime.now().strftime('%M')
      print('present time: {0}:{1}\n'.format(hour, minute))
      self.present_time = hour
      time.sleep(60)

  def stop_date_thread(self):
    """ Function to Stop Date Thread """

    self.is_started = False

  def get_present_time(self):
    """ Function to Get Present Time """

    return self.present_time

  def check_directory(self):
    """ Function to check directory """

    is_directory = os.path.isdir('./out/')
    if is_directory == False:
      os.mkdir('./out/')

    is_file = os.path.isfile('./out/table.csv')
    if is_file == False:
      comment = ['-------------------------------------------\n',
                 'Temperature & Humidity table\n',
                 '-------------------------------------------\n',
                 '\n',
                 'DATE,TIME,TEMP,HUMI\n']

      temp = open('./out/table.csv', 'w')
      for i in comment:
        temp.write(i)
      temp.close()

  def make_csv(self, temperature, humidity, directory='./out/'):
    """ Function to Make Csv """

    t, h = str(temperature) + ',', str(humidity) + ','
    date = datetime.datetime.now().strftime('%m/%d')
    time = datetime.datetime.now().strftime('%H:%M')

    saving_file = open(directory + 'table.csv', 'a')

    if self.present_time == '10':
      saving_file.write('\n')

    saving_file.write(date + ',' + time + ',' + t + h + '\n')
    saving_file.close()
    print("write csv complete!!\n")
