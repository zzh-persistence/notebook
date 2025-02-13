
import pandas as pd
import numpy as np
result_file_name = '成绩分析_结果.xlsx'
file_name = '成绩分析模版.xlsx'


def online(origin, baseline):
    if origin >= baseline:
        return 1
    else:
        return 0


df_exam1_effect = pd.read_excel(file_name, sheet_name='2次考试赋分有效分', header=1, index_col=[0, 1], nrows=5)
df_exam2_effect = pd.read_excel(file_name, sheet_name='2次考试赋分有效分', index_col=[0, 1], skiprows=8)



def process_effect(df_exam_effect):
    df_exam_effect = df_exam_effect.unstack(level=1).stack(level=0)
    df_exam_effect.reset_index(inplace=True)
    df_exam_effect.columns = ['班型', '科目', '本科', '高基']
    return df_exam_effect

df_exam1_effect = process_effect(df_exam1_effect)
df_exam2_effect = process_effect(df_exam2_effect)


df_exam1_teacher = pd.read_excel(file_name, sheet_name='任课表', header=1, index_col=0, nrows=14)
df_exam2_teacher = pd.read_excel(file_name, sheet_name='任课表', header=1, index_col=0, skiprows=17)



def process_teacher(df_exam_teacher):
    df_exam_teacher.reset_index(inplace=True)
    conditions = [df_exam_teacher['班级'].str.contains('历史')]
    choice = ['历史类']
    df_exam_teacher['班型'] = np.select(conditions, choice, default='物理类')
    df_exam_teacher['班级'] = df_exam_teacher['班级'].str.extract(r'(\d+)')
    df_exam_teacher.set_index(['班级', '班型'], inplace=True)
    df_exam_teacher = df_exam_teacher.stack()
    df_exam_teacher = pd.DataFrame(df_exam_teacher)
    df_exam_teacher.reset_index(inplace=True)
    df_exam_teacher['班级'] = df_exam_teacher['班级'].astype('float64')
    df_exam_teacher.columns = ['班级', '班型', '科目', '科任老师']
    return df_exam_teacher

df_exam2_teacher=process_teacher(df_exam2_teacher)
df_exam1_teacher=process_teacher(df_exam1_teacher)



df_exam1 = pd.read_excel(file_name, sheet_name='考试1成绩', usecols=[1, 2, 14, 17, 20, 23, 26, 31, 36, 41])
df_exam2 = pd.read_excel(file_name, sheet_name='考试2成绩', usecols=[1, 4, 8, 12, 16, 20, 24, 29, 34, 39, 44])

def process_exam(df_exam):
    df_exam = df_exam.loc[1:]
    df_exam.set_index(df_exam.columns[0], inplace=True)
    df_exam = df_exam.stack(level=0)
    df_exam = pd.DataFrame(df_exam)
    df_exam.reset_index(inplace=True)
    df_exam.columns = ['班级', '科目', '赋分']
    return df_exam


df_exam1 = process_exam(df_exam1)
df_exam2 = process_exam(df_exam2)


def analysis_exam(df_exam, df_exam_teacher, df_exam_effect):

    df_exam = df_exam.merge(df_exam_teacher[['班级', '班型']].drop_duplicates(), how='left', on=['班级'])
    df_exam = df_exam.merge(df_exam_effect, how='left', on=['班型', '科目'])
    df_exam['单上线'] = df_exam.apply(lambda x: online(x.赋分, x.本科), axis=1)
    df_exam['双上线'] = df_exam.apply(lambda x: online(x.赋分, x.高基), axis=1)
    class_avg = df_exam.groupby(['班级', '科目']).agg(实考人数=('赋分', 'count'),均分=('赋分', 'mean'),单上线 = ('单上线','sum'), 双上线=('双上线','sum'))
    class_avg = class_avg.merge(df_exam_teacher, how='left', on=['班级', '科目'])
    school_avg = df_exam.groupby('科目').agg(实考人数=('赋分', 'count'),全校均分=('赋分', 'mean'),单上线 = ('单上线','sum'), 双上线=('双上线','sum'))
    school_avg_tmp = school_avg.rename(columns={'全校均分': '均分'})
    school_avg_tmp['班级'] = '全校'
    school_avg_tmp.reset_index(inplace=True)
    class_avg = pd.concat([class_avg, school_avg_tmp])
    merged_avg = pd.merge(class_avg, school_avg['全校均分'], how='left', on='科目')
    merged_avg['均分差'] = merged_avg['均分'] - merged_avg['全校均分']
    merged_avg['离均率'] = merged_avg['均分差'] / merged_avg['全校均分']
    merged_avg['单上线率'] = merged_avg['单上线'] / merged_avg['实考人数']
    merged_avg['双上线率'] = merged_avg['双上线'] / merged_avg['实考人数']
    merged_avg.set_index(['班级', '科目'], inplace=True)
    return merged_avg.unstack(level=1).swaplevel(axis=1).sort_index(axis=1)


df_exam1_result = analysis_exam(df_exam1, df_exam1_teacher, df_exam1_effect)
df_exam2_result = analysis_exam(df_exam2, df_exam2_teacher, df_exam2_effect)
# df_exam1_result = df_exam1_result.add_prefix('考试1_')
# df_exam2_result = df_exam2_result.add_prefix('考试2_')
df_all_reslut = pd.concat([df_exam1_result, df_exam2_result], axis=1)
with pd.ExcelWriter(result_file_name, engine='openpyxl') as writer:
    df_exam1_result.to_excel(writer, sheet_name='考试1分析结果')
    df_exam2_result.to_excel(writer, sheet_name='考试2分析结果')





