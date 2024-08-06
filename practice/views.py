from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.conf import settings
from django.conf.urls.static import static
import os
from django.core.files.storage import FileSystemStorage
import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

def home(request):
  if request.method == "POST":
    file = request.FILES['file']
    uploaded_file = File.objects.create(file=file)
    return redirect('data_analysis', file_id= uploaded_file.id)
  return render(request, 'index.html')


def data_analysis(request, file_id):
    uploaded_file = get_object_or_404(File, id=file_id)
    file_path = uploaded_file.file.path
    df = pd.read_csv(file_path)
    
    dt = {'intflo': [], 'object': []}
    cols = df.columns
    for col in cols:
        if df[col].dtype in ['int64', 'float64']:
            dt['intflo'].append(col)
        else:
            dt['object'].append(col)
    
    temp = {'Parameters': dt['intflo'], 'mean': [], 'median': [], 'std': []}
    for col in temp['Parameters']:
        temp['mean'].append(round(df[col].mean(), 2))
        temp['median'].append(round(df[col].median(), 2))
        temp['std'].append(round(df[col].std(), 2))
    temp = pd.DataFrame(temp)

    summary_html = df.head(5).to_html()

    if request.method == "POST":
        form_type = request.POST.get('form_type')

        if form_type == 'numerical':
            selected_option1 = request.POST.get('selected_numeric_option1')
            selected_option2 = request.POST.get('selected_numeric_option2')

            df_selected = df[[selected_option1, selected_option2]].dropna()

            # Histogram
            plt.figure()
            df[selected_option1].hist()
            plt.title(f'Histogram of {selected_option1}')
            plt.xlabel(selected_option1)
            plt.ylabel('Frequency')
            hist_img = BytesIO()
            plt.savefig(hist_img, format='png')
            plt.close()
            hist_img.seek(0)
            hist_img_base64 = base64.b64encode(hist_img.getvalue()).decode('utf-8')

            # Boxplot
            plt.figure()
            df.boxplot(column=selected_option1)
            plt.title(f'Boxplot of {selected_option1}')
            boxplot_img = BytesIO()
            plt.savefig(boxplot_img, format='png')
            plt.close()
            boxplot_img.seek(0)
            boxplot_img_base64 = base64.b64encode(boxplot_img.getvalue()).decode('utf-8')

            # Scatter Plot
            plt.figure()
            df.plot.scatter(x=selected_option1, y=selected_option2)
            plt.title(f'Scatter Plot of {selected_option1} vs {selected_option2}')
            scatter_img = BytesIO()
            plt.savefig(scatter_img, format='png')
            plt.close()
            scatter_img.seek(0)
            scatter_img_base64 = base64.b64encode(scatter_img.getvalue()).decode('utf-8')

            context = {
                'summary_html': summary_html,
                'file_name': uploaded_file.file.name,
                'numerical_options': dt['intflo'],
                'categorical_options': dt['object'],
                'selected_numeric_option1': selected_option1,
                'selected_numeric_option2': selected_option2,
                'mean_value': round(df[selected_option1].mean(), 2),
                'median_value': round(df[selected_option1].median(), 2),
                'std_value': round(df[selected_option1].std(), 2),
                'hist_img': hist_img_base64,
                'boxplot_img': boxplot_img_base64,
                'scatter_img': scatter_img_base64
            }

        elif form_type == 'categorical':
            selected_option = request.POST.get('selected_categorical_option')

            # Mode and Unique Values
            mode_value = df[selected_option].mode()[0]
            unique_values = ', '.join(df[selected_option].unique())

            # Pie Chart
            plt.figure()
            df[selected_option].value_counts().plot.pie(autopct='%1.1f%%')
            plt.title(f'Pie Chart of {selected_option}')
            pie_chart_img = BytesIO()
            plt.savefig(pie_chart_img, format='png')
            plt.close()
            pie_chart_img.seek(0)
            pie_chart_img_base64 = base64.b64encode(pie_chart_img.getvalue()).decode('utf-8')

            context = {
                'summary_html': summary_html,
                'file_name': uploaded_file.file.name,
                'numerical_options': dt['intflo'],
                'categorical_options': dt['object'],
                'selected_categorical_option': selected_option,
                'mode_value': mode_value,
                'unique_values': unique_values,
                'pie_chart_img': pie_chart_img_base64
            }

    else:
        context = {
            'summary_html': summary_html,
            'file_name': uploaded_file.file.name,
            'numerical_options': dt['intflo'],
            'categorical_options': dt['object']
        }

    return render(request, 'viz.html', context)