import unittest

import os
import sys
import time
import os.path as op
from shutil import rmtree
from functools import partial
from kivy.clock import Clock

main_path = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.append(main_path)
from main import KrySA, ErrorPop
from tasks.manipulate import Manipulate


class Test(unittest.TestCase):
    def pause(*args):
        time.sleep(0.000001)

    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)

        # open New -> Project popup, set inputs
        app.root._new_project()
        app.root.savedlg.view.selection = [self.folder, ]
        app.root.savedlg.ids.name.text = 'Test.krysa'
        app.root.savedlg.run([self.folder, ], 'Test.krysa')
        project_folder = op.join(self.path, 'test_folder', 'Test')
        data = op.join(project_folder, 'data')
        results = op.join(project_folder, 'results')

        for x in range(4):
            # open New -> Data popup, set inputs
            app.root._new_data()
            new_data = app.root.wiz_newdata.ids.container.children[0]
            new_data.ids.table_name.text = 'NewData' + str(x)
            cols = new_data.ids.columns.children

            # set columns for new data
            range_vals = list(range(13))
            for _ in range(2):
                new_data.ids.columnadd.dispatch('on_release')
                cols[0].ids.colname.text += str(len(cols))
                cols[0].ids.coltype.text = 'INTEGER'
                vals = cols[0].ids.vals.children

                for i in range_vals:
                    cols[0].ids.valadd.dispatch('on_release')
                    vals[0].ids.value.text = str(i + 1)

                new_data.ids.columnadd.dispatch('on_release')
                cols[0].ids.colname.text += str(len(cols))
                cols[0].ids.coltype.text = 'REAL'
                vals = cols[0].ids.vals.children

                for i in range_vals:
                    cols[0].ids.valadd.dispatch('on_release')
                    num = str(i + 1)
                    vals[0].ids.value.text = num + '.' + num * x
            new_data = app.root.wiz_newdata.run()

        # (append type, overwrite, table)
        amount = 1
        options = [('Rows', False, '0'), ('Rows', True, '1'),
                   ('Columns', False, '2'), ('Columns', True, '3')]

        for opt in options:
            # check for max len of coltype's Spinner list
            self.assertTrue(amount < 5)

            taskcls = Manipulate()
            taskcls.manip_append()

            children = app.root_window.children
            for c in reversed(children):
                if 'Task' in str(c):
                    index = children.index(c)
            task = children[index]

            # fill the task
            body = task.children[0].children[0].children[0].children
            body[-1].text = 'NewData' + opt[2]
            body[-2].children[0].ids.what.text = opt[0]
            body[-2].children[0].ids.overwrite.active = opt[1]
            col_con = body[-2].children[0].ids.cols_container

            if opt[0] == 'Rows':
                body[-2].children[0].ids.amount.text = str(amount)
            elif opt[0] == 'Columns':
                col_con = col_con.children[0]
                addcol = col_con.ids.columnadd
                for z in range(amount):
                    addcol.dispatch('on_release')
                    _col = col_con.ids.columns.children[0]
                    _col.ids.colname.text = 'Column' + str(z)
                    _col.ids.coltype.text = _col.ids.coltype.values[-z]

            amount += 1
            body[-3].children[0].dispatch('on_release')

        # get results and test
        tables = app.root.tables
        exp_tables = ['NewData0', 'NewData1', 'NewData2',
                      'NewData3', 'NewData0_append_1_rows',
                      'NewData2_append_3_cols']

        # get table list from Task
        taskcls = Manipulate()
        taskcls.manip_append()

        children = app.root_window.children
        for c in reversed(children):
            if 'Task' in str(c):
                index = children.index(c)
        task = children[index]
        body = task.children[0].children[0].children[0].children
        table_values = body[-1].values
        body[-3].children[-1].dispatch('on_release')

        # check table order in tab_list and in Task
        self.assertEqual(table_values, exp_tables)
        self.assertEqual([t[0] for t in tables], exp_tables)

        _tables = [tables[4][1], tables[1][1],
                   tables[5][1], tables[3][1]]
        _exp_labels = [
            ['Data1 (A)', 'Data2 (B)', 'Data3 (C)', 'Data4 (D)'],
            ['Data1 (A)', 'Data2 (B)', 'Data3 (C)', 'Data4 (D)'],
            ['Data1 (A)', 'Data2 (B)', 'Data3 (C)', 'Data4 (D)',
             'Column0 (E)', 'Column1 (F)', 'Column2 (G)'],
            ['Data1 (A)', 'Data2 (B)', 'Data3 (C)', 'Data4 (D)',
             'Column0 (E)', 'Column1 (F)', 'Column2 (G)', 'Column3 (H)']
        ]

        for i, tbl in enumerate(_tables):
            data = tbl.rv.data
            labels = []
            for d in data:
                if 'cell' in list(d.keys()):
                    if 'label' in d['cell']:
                        labels.append(d['text'])
            self.assertEqual(labels, _exp_labels[i])
            # check for zeros/order too?

        # test saving at the end (space in table name test)
        app.root.save_project()
        app.stop()

    def test_tasks_manipulate_append(self):
        self.path = op.dirname(op.abspath(__file__))
        if not op.exists(op.join(self.path, 'test_folder')):
            os.mkdir(op.join(self.path, 'test_folder'))
        else:
            rmtree(op.join(self.path, 'test_folder'))
            os.mkdir(op.join(self.path, 'test_folder'))
        self.folder = op.join(self.path, 'test_folder')

        app = KrySA()
        p = partial(self.run_test, app)
        Clock.schedule_once(p, .000001)
        app.run()
        rmtree(self.folder)


if __name__ == '__main__':
    unittest.main()
