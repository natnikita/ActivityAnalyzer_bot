# -*- coding: utf-8 -*-

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from airium import Airium


class CourseAnalytics:
    def __init__(self, course_id):
        # Цвета для отображения графиков
        colors = [(106, 90, 205), (72, 61, 139), (75, 0, 130)]
        self.colors = ['rgb' + str(color) for color in colors]

        self.title_size = 1.15*24
        self.course_id = course_id
        self.report_path = None
        self.df_1 = pd.read_csv('course.csv')
        self.df_2 = pd.read_csv('course_module.csv')
        self.df_3 = pd.read_csv('course_element.csv')
        self.df_4 = pd.read_csv('user_course_progress.csv')
        self.df_5 = pd.read_csv('user_module_progress.csv')
        self.df_6 = pd.read_csv('user_element_progress.csv')

        course_dfs = [self.df_2, self.df_3,
                      self.df_4, self.df_5,
                      self.df_6]

        for i, df in enumerate(course_dfs):
            if 'course_id' in course_dfs[i].columns.to_list():
                course_dfs[i] = df.loc[df['course_id'] == course_id]

    def calculate_completion_rate(self):
        courses = np.array(self.df_2.course_id.unique())
        course_modules = 0
        for course in courses:
            amount = self.df_2[self.df_2.course_id == course].id.nunique()
            course_modules = amount

        is_done = {}
        for user in self.df_5.user_id.unique():
            df_current = self.df_5[self.df_5.user_id == user]
            result = df_current.is_achieved.sum()
            if course_modules == result:
                is_done[user] = 1
            else:
                is_done[user] = 0

        num_users = len(is_done)
        num_success = sum(is_done.values())

        cor = num_success / num_users

        return cor

    def plot_completion_rate_per_module(self):
        modules = self.df_5.course_module_id.unique()
        success_module = {}
        for module in modules:
            mask_2 = self.df_5.course_module_id == module
            df_module = self.df_5[mask_2]
            num = df_module.shape[0]
            num_done = df_module.is_achieved.sum()
            percent = round(100 * num_done / num)
            success_module[module] = percent

        success_module = dict(sorted(success_module.items()))

        success_module = {str(key): value for key, value in success_module.items()}

        x = list(success_module.keys())
        y = list(success_module.values())

        # fig = go.Figure(data=[go.Bar(x=x, y=y, text=y, textposition='auto')])

        # fig.update_layout(
        #     xaxis=dict(
        #         tickmode='array',
        #         tickvals=x,
        #         dtick=1,
        #         title='Индекс модуля'
        #     ),
        #     yaxis_title='Процент учеников, завершивших модуль',
        #     title='Процент учеников, завершивших каждый модуль',
        #     bargap=0.5
        # )

        fig = go.Figure(data=[go.Bar(x=x, y=y,
                        text=y, textposition='auto',
                        marker=dict(color=self.colors[0]))])

        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=x,
                dtick=1,
                title='Индекс модуля'
            ),
            yaxis=dict(
                title='Процент учеников %'
            ),
            title='Процент учеников, завершивших каждый модуль',
            title_font=dict(size=self.title_size),
            bargap=0.5,
            height=800
        )

        fig.write_html("graph_1.html")

    def calculate_task_completion_rate(self):
        rate_done = {}

        types = self.df_6.course_element_type.unique()

        for typ in types:
            df_6_type = self.df_6[self.df_6.course_element_type == typ]
            num_text = len(df_6_type)
            num_done = df_6_type[df_6_type.is_achieved == True].is_achieved.sum()
            percent = round(100 * num_done / num_text)
            rate_done[typ] = percent

        x = list(rate_done.keys())
        y = list(rate_done.values())

        fig = go.Figure(data=[go.Bar(x=x, y=y, text=y,
                        textposition='auto',
                        marker=dict(color=self.colors[0]))])

        # fig.update_layout(
        #     xaxis=dict(
        #         tickmode='array',
        #         tickvals=x,
        #         dtick=1,
        #         title='Тип задания'
        #     ),
        #     yaxis_title='Процент учеников, справившихся с заданием',
        #     title='Процент учеников, справившихся с каждым типом задания',
        #     bargap=0.7
        # )

        fig.update_layout(
            xaxis=dict(
                title='Тип задания'
            ),
            yaxis=dict(
                title='Процент учеников %'
            ),
            title='Процент учеников, справившихся с заданием',
            title_font=dict(size=self.title_size),
            bargap=0.5,
            height=800
        )

        fig.write_html("graph_2.html")

    def calculate_attempt_stats_per_module(self):
        modules = self.df_6.course_module_id.unique()
        results = []
        for module in modules:
            mask_1 = self.df_6.course_module_id == module
            df_current = self.df_6[mask_1]
            quests = df_current.course_element_type.unique()
            for quest in quests:
                mask_2 = df_current.course_element_type == quest
                num_task = df_current[mask_2].shape[0]
                num_done = df_current[(mask_2) & (df_current[mask_2]['is_achieved'] == True)].is_achieved.sum()
                percent = round(100 * num_done / num_task)
                results.append((module, quest, percent))

        df_module_success = pd.DataFrame(results, columns=["course_module_id", "course_element_type", "done_percent"])
        df_module_success = df_module_success.sort_values(by="course_module_id")
        df_module_success["course_module_id"] = df_module_success["course_module_id"].astype(str)

        fig = px.bar(df_module_success,
                     x="course_module_id",
                     y="done_percent",
                     color='course_element_type', barmode='group',
                     height=600,
                     color_discrete_map={"task": self.colors[0],
                                         "video": self.colors[1],
                                         "text": self.colors[2]})

        #fig.update_traces(marker_color=self.colors)

        fig.update_layout(
            xaxis_title="Индекс модуля",
            yaxis_title="Процент справившихся учеников",
            title="Распределение успешности учеников по каждому модулю",
            title_font=dict(size=self.title_size),
            legend_title="Тип элемента")

        # fig = px.bar(df_module_success,
        #       x="course_module_id",
        #       y="done_percent",
        #       color='course_element_type',
        #       barmode='group',
        #       height=600)

        # x = list(df_module_success["course_module_id"])

        # fig.update_layout(
        #     xaxis_title=dict(
        #         title='Индекс модуля',
        #         title_font=dict(size=1.5*12)
        #     ),
        #     yaxis_title=dict(
        #         title='Процент учеников %',
        #         title_font=dict(size=1.5*12)
        #     ),
        #     title="Распределение успешности учеников по каждому модулю",
        #     title_font=dict(size=2*24),
        #     legend_title="Тип элемента",
        #     legend_font=dict(size=1.5*12)
        # )

        fig.write_html("graph_3.html")

    def calculate_attempt_stats(self):
        mask = self.df_6.course_element_type == 'task'
        df_current = self.df_6[mask]

        modules = df_current.course_module_id.unique()
        module_tries = []
        for module in modules:
            mask_1 = df_current.course_module_id == module
            df_module = df_current[mask_1]
            tries = np.array(df_module.tries_count.unique())
            tries_min = np.min(tries)
            tries_max = np.max(tries)
            tries_avg = np.mean(tries)
            tries_med = np.median(tries)
            module_tries.append((module, tries_min, tries_max, tries_avg, tries_med))

        df_module_tries = pd.DataFrame(module_tries,
                                       columns=["course_module_id",
                                                "tries_min",
                                                "tries_max",
                                                "tries_avg",
                                                "tries_med"])

        df_module_tries = df_module_tries.sort_values(by="course_module_id")
        df_module_tries["course_module_id"] = df_module_tries["course_module_id"].astype(str)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_module_tries.course_module_id,
                             y=df_module_tries.tries_max,
                             marker=dict(color=self.colors[0]),
                             name='Максимум'))
        fig.add_trace(go.Bar(x=df_module_tries.course_module_id,
                             y=df_module_tries.tries_avg,
                             marker=dict(color=self.colors[1]),
                             name='Среднее'))
        fig.add_trace(go.Bar(x=df_module_tries.course_module_id,
                             y=df_module_tries.tries_med,
                             marker=dict(color=self.colors[2]),
                             name='Медиана'))

        fig.update_layout(
            xaxis_title="Индекс модуля",
            yaxis_title="Количество попыток",
            title="Количество попыток за каждый модуль",
            title_font=dict(size=self.title_size),
            legend_title="Тип элемента",
            height=800
        )

        x = list(df_module_tries["course_module_id"])

        # fig.update_layout(
        #     xaxis_title=dict(
        #         title='Индекс модуля',
        #         title_font=dict(size=1.5*12)
        #     ),
        #     yaxis_title=dict(
        #         title='Количество попыток',
        #         title_font=dict(size=1.5*12)
        #     ),
        #     title="Количество попыток за каждый модуль: максимум, среднее и медиана",
        #     title_font=dict(size=2*24),
        #     legend_title="Тип элемента",
        #     legend_font=dict(size=1.5*12),
        #     height=800
        # )

        fig.write_html("graph_4.html")

    def plot_attempt_histogram(self):
        mask = self.df_6.course_element_type == 'task'
        df_current = self.df_6[mask]

        # fig = px.histogram(df_current, x="tries_count",
        #                    title='Гистограмма количества попыток',
        #                    labels={'total_bill': 'total bill'},
        #                    opacity=0.8,
        #                    log_y=True,
        #                    color_discrete_sequence=self.colors[1]
        #                    )

        # fig.update_layout(
        #     xaxis_title="Количество попыток",
        #     yaxis_title="Частота количества попыток",
        # )


        fig = px.histogram(df_current,
                           x="tries_count",
                           title='Гистограмма количества попыток',
                           labels={'total_bill': 'total bill'},
                           opacity=0.8,
                           log_y=True,
                           color_discrete_sequence=[self.colors[1]]
                           )

        fig.update_layout(
                    xaxis_title="Количество попыток",
                    yaxis_title="Частота количества попыток",
                    title_font=dict(size=self.title_size),
                    height=800
        )

        fig.write_html("graph_5.html")

    def calculate_execution_time(self):
        df_5_ach = self.df_5[self.df_5.is_achieved == True]

        df_5_ach['time_created'] = pd.to_datetime(df_5_ach['time_created'])
        df_5_ach['time_achieved'] = pd.to_datetime(df_5_ach['time_achieved'])
        df_5_ach['time_unlocked'] = pd.to_datetime(df_5_ach['time_unlocked'])

        df_5_ach = df_5_ach.dropna(subset=['time_achieved', 'time_created'])
        timedelta = df_5_ach.time_achieved - df_5_ach.time_created
        hours = timedelta.dt.total_seconds() / 3600
        df_5_ach['execution_time'] = hours

        fig = px.histogram(df_5_ach, x="execution_time",
                           title='Гистограмма времени выполнения модуля',
                           labels={'total_bill': 'total bill'},
                           opacity=0.8,
                           log_y=True,
                           color_discrete_sequence=[self.colors[1]]
                           )

        fig.update_layout(
                        xaxis_title="Время (час)",
                        yaxis_title="Количество",
                        title_font=dict(size=self.title_size),
                        height=800
        )

        fig.write_html("graph_6.html")

    def to_html(self):

        cor = self.calculate_completion_rate()
        self.plot_completion_rate_per_module()
        self.calculate_task_completion_rate()
        self.calculate_attempt_stats_per_module()
        self.calculate_attempt_stats()
        self.plot_attempt_histogram()
        self.calculate_execution_time()

        a = Airium()

        # Generating HTML file

        a('<!DOCTYPE html>')
        with a.html(lang="en"):
            with a.head():
                a.meta(charset="utf-8")
                a.title(_t=f"Активности учеников курса {self.course_id}")
                a.link(rel="stylesheet", href="style.css")
            with a.body():
                with a.h1(id="main-header", kclass='main-header'):
                    a(f"Рассчитанные числовые и графические метрики для курса {self.course_id}")

                # Adding first graph
                with open('graph_1.html', 'r', encoding='utf-8') as f:
                    graph_1 = f.read()
                a(graph_1)

                # Adding second graph
                with open('graph_2.html', 'r', encoding='utf-8') as f:
                    graph_2 = f.read()
                a(graph_2)

                with open('graph_3.html', 'r', encoding='utf-8') as f:
                    graph_3 = f.read()
                a(graph_3)

                # Adding second graph
                with open('graph_4.html', 'r', encoding='utf-8') as f:
                    graph_4 = f.read()
                a(graph_4)

                with open('graph_5.html', 'r', encoding='utf-8') as f:
                    graph_5 = f.read()
                a(graph_5)

                # Adding second graph
                with open('graph_6.html', 'r', encoding='utf-8') as f:
                    graph_6 = f.read()
                a(graph_6)

                # Adding metrics
                with a.h2():
                    a("Числовые метрики")
                with a.p():
                    a("Метрика, которая показывает процент учеников, завершивших курс.")
                    a(f"COR(Completion Rate): {round(100 * cor)}%")
                    a.span(id="cor", style="font-size: 20px;")

            # Adding JavaScript to calculate metrics and update HTML elements
            with a.script():
                a.add_raw("""
                        // Getting scores data from Python
                        var scores = JSON.parse('{{ scores_json|safe }}');

                        // Calculating metrics
                        var sum = scores.reduce(function(a, b) { return a + b; });
                        var average_score = sum / scores.length;
                        var max_score = Math.max.apply(null, scores);

                        // Updating HTML elements with metrics values
                        document.getElementById('average-score').innerHTML = average_score.toFixed(2);
                        document.getElementById('max-score').innerHTML = max_score;

                        // Creating Plotly charts
                        var graph1 = document.getElementById('graph1');
                        Plotly.newPlot(graph1, JSON.parse('{{ graph1_data|safe }}'), JSON.parse('{{ graph1_layout|safe }}'));

                        var graph2 = document.getElementById('graph2');
                        Plotly.newPlot(graph2, JSON.parse('{{ graph2_data|safe }}'), JSON.parse('{{ graph2_layout|safe }}'));
                    """)

        # Encoding the file to UTF-8
        html_bytes = str(a).encode('utf-8')

        # Writing the bytes to a file
        with open('output.html', 'wb') as f:
            f.write(html_bytes)

        self.report_path = 'output.html'  # Задаем путь к созданному html-файлу

    def get_report_path(self):
        return self.report_path
