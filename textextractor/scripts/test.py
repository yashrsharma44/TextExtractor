from utils import convert_to_jpeg,convert_to_pdf

if __name__ == '__main__':
    
    print('Enter 10 names of a person')
    data_list = list()
    data_list = ['Yash', 'Piyush', 'Rohit', 'Virat', 'Rahane', 'Harry', 'Sejal', 'Umesh', 'Sid', 'Biswa']
    # for i in range(10):
    #     data_list.append(str(input('Enter {}:'.format(i+1))))
    
    print(data_list)

    pdfFile = convert_to_pdf(data_list)
    print(type(pdfFile))
    # print(pdfFile)
    convert_to_jpeg(pdfFile)
