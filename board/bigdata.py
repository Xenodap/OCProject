import json
import os.path

import pandas as pd
import pymysql
import random
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset # 텐서데이터셋
from torch.utils.data import DataLoader # 데이터로더
import numpy as np

from OCProject.settings import STATIC_DIR

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
torch.manual_seed(125)
seq_length = 2
batch = 100
data_dim = 15
hidden_dim = 15
output_dim = 1
learning_late = 0.1
epochs = 1000


def run_machine_learning():
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='ocprojectdb', charset='utf8')
    sql = 'select * from past_rockfish'

    df = pd.read_sql_query(sql, conn)
    df.to_csv('C://Bigdata/OCproject/past_rockfish_bigdata.csv', index=False)

    data = pd.read_csv('C://Bigdata/OCproject/past_rockfish_bigdata.csv')
    data['date'] = data['년도'].str.replace('년', '') + '-' + data['월'].str.replace('월', '')
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m')
    data.set_index('date', inplace=True)
    if 'Date' in data.columns:
        data.drop('Date', axis=1, inplace=True)
    data = data[['출하량(톤)', '경남출하량(톤)', '전남출하량(톤)', '기타출하량(톤)', '양성물량(만 마리)',
                  '전남산지가격(원/kg)', '인천도매가격(원/kg)', '하남도매가격(원/kg)', '부산도매가격(원/kg)',
                 '완도수온(℃)', '통영수온(℃)', '총 수출금액', '총 수입금액', '연어수입중량(kg)','통영산지가격(원/kg)']]

    data['통영산지가격(원/kg)'] = data['통영산지가격(원/kg)'].astype(int)
    data['전남산지가격(원/kg)'] = data['전남산지가격(원/kg)'].astype(int)
    data['인천도매가격(원/kg)'] = data['인천도매가격(원/kg)'].astype(int)
    data['하남도매가격(원/kg)'] = data['하남도매가격(원/kg)'].astype(int)
    data['부산도매가격(원/kg)'] = data['부산도매가격(원/kg)'].astype(int)


    train_size = int(len(data) * 0.9)
    train_set = data[0:train_size]
    test_set = data[train_size - seq_length:]

    scaler_x = MinMaxScaler()
    scaler_x.fit(train_set.iloc[:, :-1])

    train_set.iloc[:, :-1] = scaler_x.transform(train_set.iloc[:, :-1])
    test_set.iloc[:, :-1] = scaler_x.transform(test_set.iloc[:, :-1])

    # output scale
    scaler_y = MinMaxScaler()
    scaler_y.fit(train_set.iloc[:, [-1]])
    train_set.iloc[:, -1] = scaler_y.transform(train_set.iloc[:, [-1]])
    test_set.iloc[:, -1] = scaler_y.transform(test_set.iloc[:, [-1]])


    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(125)


    trainX, trainY = build_dataset(np.array(train_set), seq_length)
    testX, testY = build_dataset(np.array(test_set), seq_length)

    trainX_tensor = torch.FloatTensor(trainX)
    trainY_tensor = torch.FloatTensor(trainY)
    testX_tensor = torch.FloatTensor(testX)
    testY_tensor = torch.FloatTensor(testY)

    train_dataset = TensorDataset(trainX_tensor, trainY_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch, shuffle=True,
                              drop_last=True)


    net = Net(data_dim, hidden_dim, seq_length, output_dim, 1)
    model, train_hist = train_model(net, train_loader, epochs=epochs,
                                    lr=learning_late, verbos=20, patience=100)

    fig = plt.figure(figsize=(10, 6))
    plt.plot(train_hist, label='Training loss')
    plt.legend()

    path = "C://Bigdata/OCproject/OCResult.pth"
    torch.save(model.state_dict(), path)

    model = Net(data_dim, hidden_dim, seq_length, output_dim, 1).to(device)
    model.load_state_dict(torch.load(path), strict=False)
    model.eval()

    with torch.no_grad():
        pred = []
        for pr in range(len(testX_tensor)):
            model.reset_hidden_state()
            predicted = model(torch.unsqueeze(testX_tensor[pr], 0))
            predicted = torch.flatten(predicted).item()
            pred.append(predicted)

        pred_inverse = scaler_y.inverse_transform(np.array(pred).reshape(-1, 1))
        testY_inverse = scaler_y.inverse_transform(testY_tensor)

    test_set['YearMonth'] = test_set.index.strftime('%Y-%m')

    # 'YearMonth' 열을 datetime 형식으로 변환
    test_set['YearMonth'] = pd.to_datetime(test_set['YearMonth'])

    # 'YearMonth' 열을 예측값과 실제값의 길이에 맞게 잘라줍니다
    test_set = test_set[:len(pred_inverse)]

    # 예측값과 실제값의 길이를 'YearMonth'와 일치시킴
    pred_inverse = pred_inverse[:len(test_set)]
    testY_inverse = testY_inverse[:len(test_set)]


    print(os.path.join(STATIC_DIR,'images/bigdata_fish.png'))
    fig = plt.figure(figsize=(6, 6))
    plt.plot(test_set['YearMonth'], pred_inverse, label='pred')
    plt.plot(test_set['YearMonth'], testY_inverse, label='true')
    plt.xticks(rotation=45)  # x축 레이블을 45도 회전하여 가독성 향상
    plt.legend()

    plt.savefig(os.path.join(STATIC_DIR,'images/bigdata_fish.png'))



def build_dataset(time_series, seq_length):
    dataX=[]
    dataY=[]
    for i in range(0, len(time_series)-seq_length):
        x_=time_series[i:i+seq_length, :]
        y_=time_series[i+seq_length,[-1]]
        dataX.append(x_)
        dataY.append(y_)
    return np.array(dataX), np.array(dataY)


class Net(nn.Module):
  def __init__(self, input_dim, hidden_dim, seq_length, output_dim, layers):
    super(Net, self).__init__()
    self.hidden_dim=hidden_dim
    self.seq_length=seq_length
    self.output_dim=output_dim
    self.layers=layers

    self.lstm=nn.LSTM(input_dim,
                      hidden_dim,
                      num_layers=layers,
                      batch_first=True)
    self.fc=nn.Linear(hidden_dim, output_dim, bias=True)

  def reset_hidden_state(self):
    self.hidden=(
      torch.zeros(self.layers, self.seq_length, self.hidden_dim),
      torch.zeros(self.layers, self.seq_length, self.hidden_dim)
    )
  def forward(self, x):
    x, _status=self.lstm(x)
    x=self.fc(x[:, -1])
    return x


def train_model(model, train_df, epochs=None, lr=None, verbos=10, patience=10):
    criterion = nn.MSELoss().to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_late)
    n_epochs = epochs

    train_hist = np.zeros(n_epochs)
    for epoch in range(n_epochs):
        avg_cost = 0
        total_batch = len(train_df)

        for batch_idxm, sample in enumerate(train_df):
            x_train, y_train = sample
            model.reset_hidden_state()
            output = model(x_train)
            loss = criterion(output, y_train)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            avg_cost += loss / total_batch

        train_hist[epoch] = avg_cost

        if epoch % verbos == 0:
            print('Epoch:{}, train_loss:{}'.format(epoch, avg_cost.item()))

        if (epoch % patience == 0) & (epoch != 0):
            if train_hist[epoch - patience] < train_hist[epoch]:
                print("Early Stopping")
                break
    return model.eval(), train_hist

def returnToJson(board):
    jsonData = []
    for data in board:
        dictionary = {
        #   우럭-통영-월-산지 리턴해야함
        }
        jsonData.append(dictionary)

    return json.dumps(jsonData)

def MAE(true, pred):
    return np.mean(np.abs(true-pred))