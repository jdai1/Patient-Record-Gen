#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import reportlab
import numpy as np
import pyreadstat
np.__version__


# In[2]:


from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, BaseDocTemplate, Frame, PageTemplate, NextPageTemplate, PageBreak, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm


# In[3]:


# DATA EXTRACTION


# In[4]:


input_file_path = '/Users/Julian/Documents/Github/Patient-Record-Gen/Input/SourceData/'
input_dm = input_file_path + r'demo.sas7bdat'
input_pe = input_file_path + r'pege.sas7bdat'
input_ae = input_file_path + r'advevnts.sas7bdat'
input_ds = input_file_path + r'conmeds.sas7bdat'


# In[49]:


# meta data
dm_meta = pyreadstat.read_sas7bdat(input_dm)
pe_meta = pyreadstat.read_sas7bdat(input_pe)
ae_meta = pyreadstat.read_sas7bdat(input_ae)
ds_meta = pyreadstat.read_sas7bdat(input_ds)


# In[50]:


dm_dict = dict()
for i in range(0, len(dm_meta[1].variable_measure.keys())):
    oid = list(dm_meta[1].variable_measure.keys())[i]
    label = dm_meta[1].column_labels[i]
    dm_dict[oid] = label
    
pe_dict = dict()
for i in range(0, len(pe_meta[1].variable_measure.keys())):
    oid = list(pe_meta[1].variable_measure.keys())[i]
    label = pe_meta[1].column_labels[i]
    pe_dict[oid] = label

ae_dict = dict()
for i in range(0, len(ae_meta[1].variable_measure.keys())):
    oid = list(ae_meta[1].variable_measure.keys())[i]
    label = ae_meta[1].column_labels[i]
    ae_dict[oid] = label
ds_dict = dict()
for i in range(0, len(ds_meta[1].variable_measure.keys())):
    oid = list(ds_meta[1].variable_measure.keys())[i]
    label = ds_meta[1].column_labels[i]
    ds_dict[oid] = label


# In[7]:


# use pandas directly to extract data from sas7bdat files
dm = pd.read_sas(input_dm, format='sas7bdat', encoding='latin-1')
pe = pd.read_sas(input_pe, format='sas7bdat', encoding='latin-1')
ae = pd.read_sas(input_ae, format='sas7bdat', encoding='latin-1')
ds = pd.read_sas(input_ds, format='sas7bdat', encoding='latin-1')


# In[8]:


pd.set_option("display.max_rows", None, "display.max_columns", None)


# In[10]:


dm.shape


# In[11]:


pe.shape


# In[12]:


ae.shape


# In[13]:


ds.shape


# In[14]:


subj_id = 1.0
site_num = dm[dm['SUBJID'] == subj_id].iloc[0]['SITE']
date = 'Data Extracted Date: xxx'
site_num


# In[15]:


import math


# In[43]:


# DATA MANIPULATION


# In[44]:


subj_dm = dm[dm['SUBJID'] == subj_id]
dm_data = subj_dm[['DOB', 'SEX', 'RACE', 'RACESP', 'PRDIAG', 'WGT', 'HGT']]
dm_data.rename(columns={'DOB':'Date of Birth:', 'SEX':'Sex:', 'PRDIAG':'Pre-Diagnosis:', 'WGT':'Weight:', 'HGT':'Height:'}, inplace=True)
dm_data = dm_data.iloc[0].to_frame().T
if (math.isnan(dm_data['RACESP'])):
     dm_data['Race (Specify if other):'] = dm_data['RACE']
else:
    dm_data['Race (Specify if other):'] = dm_data['RACESP']
    
dm_data = dm_data[['Date of Birth:', 'Sex:', 'Race (Specify if other):', 'Pre-Diagnosis:', 'Weight:', 'Height:']]
dm_table = dm_data.iloc[0].to_frame()
dm_table.reset_index(inplace=True)
# rename columns to allow them to be cocatenated together
dm_table.rename(columns={'index':'Key', 0:'Value'}, inplace=True)


# In[45]:


subj_ds = ds[ds['SUBJID'] == subj_id]
ds_data = subj_ds[['MEDNAME', 'STARTDT', 'ENDDT', 'INDIC', 'ROUTE', 'ONGOING']]
ds_data = ds_data.iloc[0].to_frame().T
ds_data.rename(columns={'MEDNAME':'Medicine Name:', 'STARTDT':'Start Date:', 'ENDDT':'End Date:', 
                        'INDIC':'Indicated:', 'ROUTE':'Route:', 'ONGOING':'Ongoing'}, inplace=True)
ds_data.reset_index(drop=True, inplace=True)
# fix this
ds_table = ds_data.loc[0].to_frame()
ds_table.reset_index(inplace=True)
# rename columns to allow them to be cocatenated together
ds_table.rename(columns={'index':'Key', 0:'Value'}, inplace=True)


# In[47]:


subj_pe = pe[pe['SUBJID'] == subj_id]
pe_data = subj_pe.iloc[0].to_frame().T
pe_data = pe_data[['PE1', 'PE2', 'PE3', 'PE4', 'BP_SYS', 'BP_DIA', 'PULSE', 'RESPRATE']]
pe_data['Blood pressure:'] = pe_data['BP_SYS'] + '/' + pe_data['BP_DIA']
pe_data.rename(columns={'PE1':'Physical Exam 1:', 'PE2':'Physical Exam 2:', 'PE3':'Physical Exam 3:', 'PE4':'Physical Exam 4:',
                        'PULSE':'Pulse:', 'RESPRATE':'Respiratory rate:'}, inplace=True)



pe_data = pe_data[['Physical Exam 1:','Physical Exam 2:', 'Physical Exam 3:', 'Physical Exam 4:', 
                  'Pulse:', 'Respiratory rate:', 'Blood pressure:']]

pe_data.reset_index(drop=True, inplace=True)
# convert to table
pe_table = pe_data.iloc[0].to_frame()
pe_table.reset_index(inplace=True)
# rename columns to allow them to be cocatenated together
pe_table.rename(columns={'index':'Key', 0:'Value'}, inplace=True)


# In[20]:


def makeFlowable(table):
    # allows autowrapping --> input the data as report lab flowables instead of simple text
    # prevents aliasing
    labelStyle = ParagraphStyle('Normal',
                                fontSize=10,
                                fontName='Times-Roman',
                                textColor=colors.darkblue)
                                
    dataStyle = ParagraphStyle('Normal',
                                fontSize=10,
                                fontName='Times-Roman',
                                textColor=colors.black
                                )
    flowable = table.copy(deep=True)
    for c in range(0, table.shape[1]):
        for r in range(0, table.shape[0]):
            # replace each value in the dataframe with a reportlab Paragraph containing its contents
            if c % 2 == 0:
                flowable.iloc[r, c] = Paragraph(flowable.iloc[r, c], labelStyle)
            elif c % 2 == 1:
                flowable.iloc[r, c] = Paragraph(flowable.iloc[r, c], dataStyle)
    return flowable


# In[21]:


# convert the extracted data into Paragraph objects to allow autowrapping 
dm_flowable = makeFlowable(dm_table.astype(str))
tr_flowable = makeFlowable(ds_table.astype(str))
ds_flowable = makeFlowable(pe_table.astype(str))

dmdspe_table = pd.concat([dm_flowable, tr_flowable, ds_flowable], axis=1)
labels = pd.DataFrame([['1 - BASIC INFORMATION', '', '', '', '', ''], ['Demography', '','Disposition', '', 'Physical Exam', '']], 
                              columns=['Key', 'Value', 'Key', 'Value', 'Key', 'Value'])
dmdspe_table = labels.append(dmdspe_table)
dmdspe_table = dmdspe_table.replace(np.nan, '', regex=True)
dmdspe_table.reset_index(drop=True, inplace=True)


# In[48]:


subj_ae = ae[ae['SUBJID'] == subj_id]
ae_data = subj_ae[['AE_1', 'SAE_1', 'STRTDT_1', 'STOPDT_1', 'ONGO_1', 'SEV_1', 'REL_1', 'OUTC_1', 'AE_2', 'SAE_2', 
                   'STRTDT_2', 'STOPDT_2', 'ONGO_2', 'SEV_2', 'REL_2', 'OUTC_2']]
ae_data.rename(columns={'AE1':'Adverse Event 1:', 'SAE1':'Serious AE 1:', 'STRTDT_1':'Start Date:', 'STOPDT_1':'Stop Date:', 
                        'ONGO_1':'Ongoing:', 'SEV_1':'Severity:', 'REL_1':'Relationship:', 'OUTC_1':'Outcome:', 'AE2':'Adverse Event 2:', 
                        'SAE2':'Serious AE 2:', 'STRTDT_2':'Start Date:', 'STOPDT_2':'Stop Date:', 'ONGO_2':'Ongoing:',
                        'SEV_2':'Severity', 'REL_2':'Relationship', 'OUTC_2':'Outcome'}, inplace=True)

ae_data.reset_index(drop=True, inplace=True)
# create a list of dataframes to encompass several different adversity events
ae_data_list = []
for i in range(0, ae_data.shape[0]):
    specific_ae_event = ae_data.iloc[i].to_frame()
    specific_ae_event.reset_index(inplace=True)
    #specific_ae_event.rename(columns={'index':'Key', 0:'Value'}, inplace=True)
    
    # restructure df to fit into pdf
    event_df = specific_ae_event.iloc[:8]
    event_df.reset_index(drop=True, inplace=True)
    state_df = specific_ae_event.iloc[8:]
    state_df.reset_index(drop=True, inplace=True)
    specific_ae_event_df = pd.concat([event_df, state_df], axis=1)
    specific_ae_event_df.columns = ['Key', 'Value', 'Key', 'Value']
    
    ae_data_list.append(specific_ae_event_df)


# In[24]:


# create a list of tables as input into the table
ae_table_list = []
i = 1
for ae_df in ae_data_list:
    ae_flowable = makeFlowable(ae_df.astype(str))
    labels = pd.DataFrame([['2 - ADVERSE EVENT (' + str(i) + ')', '', '', ''], ['Event', '','State', '']], 
                                  columns=['Key', 'Value', 'Key', 'Value'])
    ae_table = labels.append(ae_flowable)
    ae_table = ae_table.replace(np.nan, '', regex=True)
    ae_table.reset_index(drop=True, inplace=True)
    ae_table_list.append(ae_table)
    i += 1


# In[29]:


# input
#--> autowrapping example
#df_list = [dmdspe_flowable] 
df_list = [dmdspe_table]
for table in ae_table_list:
    df_list.append(table)


# In[30]:


# report lab pdf generation
#
#


# In[37]:


# base doc template is more customizable than simple doc template, which provides a set template and frame layout
# the margins define the area of the pdf that can be written on while the pagesize defines the actual size of the pdf
doc = BaseDocTemplate("/Users/Julian/Documents/GitHub/Patient-Record-Gen/Output/output.pdf", 
                      topMargin=1*inch, bottomMargin=1*inch, rightMargin=0.2*inch, leftMargin=0.2*inch, 
                      pagesize= (15*inch, 13*inch))

# the frame defines an area that flowables such as tables can be added to
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.rightMargin, doc.height - 0.75*inch, id='data')
doc.height


# In[38]:


element = []

# adding the page template 'report' to the doc
element.append(NextPageTemplate('report'))

available_height = frame.height

table_style = TableStyle([
                        # merge top row to form label
                        ('SPAN', (0, 0), (-1, 0)),
                        #padding for all boxes for readability
                        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        
                        #background colors
                        ('BACKGROUND', (0, 1), (-1, 1), colors.royalblue),
    
    
                        #fonts
                        ('FONT', (0, 0), (0, 0), 'Times-Roman', 13),
                        ('FONT', (0, 1), (-1, 1), 'Times-Roman', 11),

                        #textcolors
                        ('TEXTCOLOR', (0, 0), (0, 0), colors.darkblue),
                        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
    
    
                        #grid
                        ('INNERGRID', (0,0), (-1,-1), 1, colors.black), 
                        ('BOX', (0,0), (-1,-1), 1, colors.black)])

table_style_bot = TableStyle([
                        #padding for all boxes for readability
                        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        
                        #background colors
                        ('BACKGROUND', (0, 0), (-1, 0), colors.royalblue),
    
                        #fonts
                        ('FONT', (0, 0), (-1, 0), 'Times-Roman', 11),
    
                        #textcolors
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    
                        #grid
                        ('INNERGRID', (0,0), (-1,-1), 1, colors.black), 
                        ('BOX', (0,0), (-1,-1), 1, colors.black)])

# create specific labels by merging boxes and setting text colors
# use foreloop because each table will likely vary in size
def setTableStyle(nparray, table):
    for i in range(nparray.shape[1]):
        if i % 2 == 0:
            table.setStyle(TableStyle([('SPAN', (i, 1), (i + 1, 1))]))

# used in the case that a table is split across two pages. Since that table slightly varies,
# a new function must be created to filter it
def setTableStyleBot(nparray, table):
    for i in range(nparray.shape[1]):
        if i % 2 == 0:
            table.setStyle(TableStyle([('SPAN', (i, 0), (i + 1, 0))]))  
index = 0
spacer = 0.5*inch
numPages = 1

for df in df_list:
    # example of adding image in between tables
    #image = Image("/Users/Julian/Documents/CompSci/Numedi-Internship/2020/PatientRecordGen/Input/disney.png")
    #image.hAlign = 'LEFT'
    #element.append(image)
    #available_height -= image.wrap(0, available_height)[1]
    
    nparray = np.array(df)
    table = Table(nparray.tolist(), columnWidths[index])
    table.hAlign = 'LEFT'
    # general style
    setTableStyle(nparray, table)
    # specific style that vary from each table
    table.setStyle(table_style)
    table_height = table.wrap(0, available_height)[1]
    
    npheader = np.array(df.iloc[0:3])
    print(columnWidths[index][0:3])
    header_table = Table(npheader.tolist(), columnWidths[index][0:3])
    
    if available_height <= header_table.wrap(0, available_height)[1]:
        #print(1)
        # go to new page if there is not enough space for a single row of data
        available_height = frame.height
        element.append(PageBreak())
        numPages += 1

    elif (table_height <= available_height):
        #print(2)
        element.append(table)
        element.append(Spacer(0, spacer))
        available_height = available_height - table_height - spacer
        
    else:
        #print(3)
        # loop through number of rows starting from last and do wrap until the table height is <=
        # individual height. then separate rows from there and reconstruct table in separate pages
        for i in range(1, nparray.shape[0]):
            # top dataframe
            df1 = df.iloc[0:nparray.shape[0] - i]
            df1.reset_index(drop=True, inplace=True)
            nparray1 = np.array(df1)
            table1 = Table(nparray1.tolist(), columnWidths[index])
            table1.hAlign = 'LEFT'
            
            setTableStyle(nparray1, table1)
            table1.setStyle(table_style)
            
            # extract labels from first df and transpose it to be concatenated on the other df
            labels = df1.loc[1].to_frame()
            labels = labels.T
        
            # bottom dataframe
            df2 = df.iloc[nparray.shape[0] - i:nparray.shape[0]]
            df2.reset_index(drop=True, inplace=True)
            df2 = pd.concat([labels, df2])
            nparray2 = np.array(df2)
            table2 = Table(nparray2.tolist(), columnWidths[index])
            table2.hAlign = 'LEFT'
            
            setTableStyleBot(nparray2, table2)
            table2.setStyle(table_style_bot)
            
            # if the top dataframe will fit in the remaining space, add it to the pdf
            # then add the bottom df to a new page
            if (table1.wrap(0, available_height)[1] < available_height - 23):
                element.append(table1)
                element.append(PageBreak())
                numPages += 1
                element.append(table2)
                element.append(Spacer(0, spacer))
                available_height = frame.height - table2.wrap(0, available_height)[1] - spacer
                break
    index += 1


# In[39]:


"""
Clarifications on using the x-y coordinates to adjust elements on the pdf:

doc is defined with topMargin=1*inch, bottomMargin=1*inch, rightMargin=0.2*inch, leftMargin=0.2*inch, pagesize= (15*inch, 13*inch)

To align with the doc margins, the frame in which data is appended to, uses the same left, right, and bottom margins
as the doc. The frame's top margin is 0.75 inches lower than the top margin of the doc to allow space for the patient name

doc.height and doc.width describe the space within the margins of the doc. Therefore, for example, to find the total
width of the pdf, add doc.width to doc.leftMargin and doc.rightMargin. These values are represetned as floats, so
addition applies to them.

On a canvas, (0, 0) represents the lower left hand corner. To place an element at the right hand side of the page, 
the x value should be close to doc.width. To place an element at the top of the page, the y value should be close to
doc.height. 

"""


# In[51]:


# the header function receives the canvas and the doc as parameters
# this code is very similar to your version of the myheader function, with the exception of a few minor changes
def header(canvas, doc):
    canvas.saveState()
    logo = "/Users/Julian/Documents/GitHub/Patient-Record-Gen/Input/gnu.png"
    horizon_mgin = 20
    canvas.setFont('Times-Roman', 10.5)
    canvas.setLineWidth(.3)
    # x-y coordinates of the logo, starting from the lower left hand corner
    # The logo's size is changed by changing its width. The heigh will resize to preserve the ratio of the png
    canvas.drawImage(logo, horizon_mgin, doc.bottomMargin + doc.height + 5, width=0.6*inch, preserveAspectRatio=True)
    # in drawString, the first two parameters specify the x-y coordinates
    canvas.drawString(horizon_mgin, doc.height + doc.bottomMargin, "Numedi" )
    canvas.drawString(horizon_mgin, doc.height + doc.bottomMargin - 15, "Protocol Snow White" )
    canvas.drawRightString(doc.width + doc.leftMargin + doc.rightMargin - horizon_mgin, doc.height + doc.bottomMargin, "Page %d of %d" % (doc.page, numPages))
    canvas.drawRightString(doc.width + doc.leftMargin + doc.rightMargin - horizon_mgin, doc.height + doc.bottomMargin - 15, date)
    canvas.setFont('Times-Italic', 11)
    canvas.drawCentredString(doc.width/2.0, doc.height + doc.bottomMargin, "Confidential")
    canvas.setFont('Times-Roman', 14)
    canvas.drawCentredString(doc.width/2.0, doc.height + doc.bottomMargin - 30, "PATIENT %s %s" % (subj_id, site_num))
    canvas.restoreState()


# In[52]:


# the frame is then added to a page template which is in turn added to the doc itself
template = PageTemplate(id='report', frames=frame, onPage=header)
doc.addPageTemplates([template])


# In[53]:


# supply the formatted tables into the doc
doc.build(element)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




