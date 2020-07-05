# Patient-Record
Given raw patient data, filter and manipulate the data and provide a pdf of collective patient information. The PDF should be formatted in a way that separates different sections such as adversity events, demographics, disposition, and other genres of information. 

## Installation
Download or clone the repository to the preferred location. 
Dependencies:
- Pandas
- ReportLab
- Numpy

## Usage
A sample input data is included,  To use the data manipulation on other data sets, the data manipulation section of the jupyter notebook should be modified. However, the pdf creation, formatting, and aescethics will automatically format to any dataframe passed in. Search the notebook for any other features that need to be customized. The finished output.pdf is located in the output folder.

## How it works
Using pandas, the raw data sas7bdat files are processed and manipulated to obtain the desired section of information. Then, the data, now within a dataframe, is used to create a Table object in report lab, which is then flowed into the output pdf. To learn more about the details, observe the notebook.

## Credits
Project completed under the guidance of Numedi. 

Enjoy!
