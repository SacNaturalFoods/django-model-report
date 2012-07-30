# -*- coding: utf-8 -*-
from model_report.highcharts.base import true, false, null, DictObject
from model_report.highcharts.options import get_highchart_data


class HighchartRender(object):

    def reset(self):
        self.model = DictObject(**get_highchart_data())

    def __init__(self, config):
        self.reset()
        self.config = config

    def set_pie_chart_options(self, report_rows):
        funcs_op = {
            'sum': sum,
            'max': max,
            'min': min,
            'len': len,
            'avg': lambda vlist: sum(vlist) / len(vlist)
        }
        serie_operation = funcs_op[self.config['serie_op']]

        if self.config['has_group_totals']:
            serie_data = []
            for grouper, rows in report_rows:
                add_group = True
                if self.config['has_report_totals']:
                    if len(rows) <= 2:
                        add_group = False
                if not add_group:
                    continue
                serie_values = []
                for r in rows:
                    if r.is_value():
                        serie_values.append(r[self.config['serie_field']].value)

                value = serie_operation(serie_values)

                serie_data.append([grouper, round(value, 2)])
            data = self.model.serie_obj.create(**{
                'name': grouper,
                'data': serie_data,
                'type': 'pie',
            })
            self.model.series.add(data)

        self.model.chart.renderTo = 'container'
        self.model.chart.plotBackgroundColor = null,
        self.model.chart.plotBorderWidth = null,
        self.model.chart.plotShadow = false

        self.model.title.text = self.config['title']
        self.model.tooltip.formatter = "function() { return roundVal(this.percentage) + ' %'; }"

        self.model.plotOptions.pie.allowPointSelect = true
        self.model.plotOptions.pie.cursor = 'pointer'
        self.model.plotOptions.pie.dataLabels.enabled = true
        self.model.plotOptions.pie.dataLabels.color = '#000000'
        self.model.plotOptions.pie.dataLabels.connectorColor = '#000000'
        repr_char = '$'
        repr_fun = 'fm'
        if self.config['serie_op'] == 'len':
            repr_char = ''
            repr_fun = ''
        self.model.plotOptions.pie.dataLabels.formatter = "function() { return '<b>'+ this.point.name +'</b>: %s '+ %s(this.point.y); }" % (repr_char, repr_fun)

    def set_bar_chart_options(self, report_rows):
        pass

    def is_valid(self):
        if self.config:
            if self.config['serie_field']:
                return True
        return False

    def get_chart(self, report_rows):
        self.reset()
        if report_rows and self.is_valid():
            if self.config['chart_mode'] == 'pie':
                self.model.credits.enabled = false
                self.set_pie_chart_options(report_rows)
            if self.config['chart_mode'] == 'column':
                self.model.credits.enabled = false
                self.set_bar_chart_options(report_rows)
        return self

    @property
    def options(self):
        from django.utils import simplejson
        json = unicode(self.model)
        json = simplejson.dumps(json)[1:-1]
        json = json.replace("'true'", 'true')
        json = json.replace("'false'", 'false')
        json = json.replace("'null'", 'null')
        json = json.replace('\\"', '')
        json = json.replace('},', '},\n\t')
        json = json.replace('[{', '[\n\t{')
        json = json.replace('}]', '}\n]')
        json = json.replace("u'", "'")
        return json