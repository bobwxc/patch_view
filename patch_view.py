#!/usr/bin/env python3
from sys import argv
import argparse


def find_diff_header(diff_text, i=0):
    n = len(diff_text)
    x1 = -1
    x2 = -1
    x3 = -1
    while(i < n):
        if diff_text[i][0:4] == 'diff':
            x1 = i
            print(diff_text[i], end='')
        if x1 != -1 and diff_text[i][0:3] == '---':
            x2 = i
            if x2 != -1 and x1 == -1:
                x1 = x2 # 预防有的没有 diff 行
            print(diff_text[i], end='')
        if x1 != -1 and diff_text[i][0:3] == '+++':
            x3 = i
            print(diff_text[i], end='')
            if x1 != -1 and x2 != -1 and x3 != -1:
                return (x1, x2, x3)
        i += 1
    if x1 == -1 or x2 == -1 or x3 == -1:
        # raise SyntaxError('error diff header')
        return (-1, -1, -1)
    return (x1, x2, x3)


def find_atat(diff_text, i=0):
    n = len(diff_text)
    atat = -1
    f1 = -1
    f1_ = -1
    f2 = -1
    f2_ = -1
    while(i < n):
        if diff_text[i][0:2] == '@@':
            # eg: @@ -1,27 +1,31 @@
            # 原始文件 开始行，持续行 修改后文件 开始行，持续行
            #          f1      f1_               f2      f2_
            if diff_text[i].find(',') == -1:
                raise SyntaxError('error line "@@ xx,xx..."')
            else:
                atat = i
            f1 = int(diff_text[i][diff_text[i].find(
                '-')+1:diff_text[i].find(',')])
            f1_ = int(diff_text[i][diff_text[i].find(
                ',')+1:diff_text[i].find('+')-1])

            f2 = int(diff_text[i][diff_text[i].find(
                '+')+1:diff_text[i].rfind(',')])
            f2_ = int(diff_text[i][diff_text[i].rfind(
                ',')+1:diff_text[i].rfind(' @@')])

            return (atat, f1, f1_, f2, f2_)
        i += 1
    if atat == -1 or f1 == -1 or f1_ == -1 or f2 == -1 or f2_ == -1:
        # raise SyntaxError('error diff header')
        return (-1, -1, -1, -1, -1)

    return (atat, f1, f1_, f2, f2_)


def copy_append(origin_text, start, end, modify_text):
    # print(modify_text)
    i = start
    while i < len(origin_text) and i < end:
        a = [origin_text[i], 0]
        if a != []:
            modify_text.append(a)
        i += 1
    return modify_text


def modify(origin_text, diff_text, atat, modify_text):
    i = atat[0]+1
    while(i < len(diff_text)):
        # 0 = 1 + 2 -
        if diff_text[i][0] == '+':
            a = [diff_text[i][1:], 1]
            modify_text.append(a)
        elif diff_text[i][0] == '-':
            a = [diff_text[i][1:], 2]
            modify_text.append(a)
        elif diff_text[i][0] == ' ':
            a = [diff_text[i][1:], 0]
            modify_text.append(a)
        elif diff_text[i][0:2] == '@@':
            return modify_text
        i += 1
    return modify_text


def one_diff(origin_text, diff_text, modify_text, atat, diff_header):
    if atat[1] > 1:
        modify_text = copy_append(origin_text, 1-1, atat[1]-1, modify_text)

    diff_header_ = find_diff_header(diff_text, diff_header[0]+1)
    while True:
        modify_text = modify(origin_text, diff_text, atat, modify_text)
        atat_ = atat
        atat = find_atat(diff_text, atat_[0]+1)
        if (atat[0] > diff_header_[0] and diff_header_[0] != -1) or atat[0] == -1:
            modify_text = copy_append(
                origin_text, atat_[1]+atat_[2]-1, len(origin_text), modify_text)
            break
        modify_text = copy_append(
            origin_text, atat_[1]+atat_[2]-1, atat[1]-1, modify_text)
    return modify_text


def output_file(modify_text, filepath='./modify_file', type_=0):
    modify_file = open(filepath, 'w')
    if type_ == 0:  # 输出改动
        for i in modify_text:
            modify_file.write(str(i[1])+' '+i[0])
    elif type_ == 1:  # 输出新文件
        for i in modify_text:
            if i[1] != 2:
                modify_file.write(i[0])
    elif type_ == 2:  # 输出旧文件
        for i in modify_text:
            if i[1] != 1:
                modify_file.write(i[0])


def output_html(diff_header, diff_text, modify_text, filepath='./html_file.html'):
    import json
    import time
    html_file = open(filepath, 'w')
    var = {
        'title': diff_text[diff_header[0]],
        'time': time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()),
        'comment': '',
        'file': diff_text[diff_header[0]],
        'change': diff_text[diff_header[1]]+diff_text[diff_header[2]],
        'content': modify_text
    }
    # var=json.dumps(var,sort_keys=True, indent=4, separators=(',', ': '))
    var = json.dumps(var)

    html_text = '''<!DOCTYPE html>

<html>

<head>
    <meta charset="utf-8">
    <meta name='viewport' content='width=device-width initial-scale=1'>
    <title>patch view</title>
    <style>
        :root {
            font-size: 15px;
        }

        html {
            background-color: rgb(243, 243, 243);
        }

        body {
            margin: auto;
            padding: 1rem 1rem 1rem 1rem;
            max-width: 60rem;
        }

        header {
            padding: 0.1rem 1rem 0.1rem 1rem;
            border-radius: 0.5rem;
            background-color: rgba(191, 255, 191, 0.6);
        }

        article {
            padding: 0.1rem 1rem 1rem 1rem;
            border-radius: 0.5rem;
            background-color: rgba(255, 255, 255, 0.6);
        }

        section.code_head {
            border-radius: 0.1rem;
            background-color: rgb(243, 243, 243);
        }

        section.code_content {
            border-radius: 0.1rem;
            border: 1px solid rgb(201, 201, 201);
            overflow-x: auto;
        }

        table.code {
            width: 100%;
        }

        col.num {
            width: max-content;
            font-size: 1rem;
            color: rgb(60, 60, 60);
        }

        td.num {
            text-align: right;
            user-select:none;
        }

        col.status {
            width: max-content;
            text-align: center;
            font-size: 1rem;
            color: rgb(60, 60, 60);
        }

        td.status {
            text-align: center;
            background-color: rgb(201, 201, 201);
            user-select:none;
        }

        col.code {
            min-width: 80%;
        }

        td.increase {
            background-color: rgb(102, 245, 164);
        }

        td.decrease {
            background-color: rgb(252, 150, 150);
        }

        #powerby {
            text-align: center;
            color: rgb(60, 60, 60);
        }
    </style>
</head>

<body>
    <header>
        <h1 class="title" id="header_title">title</h1>
        <p class="time" id="header_time">time</p>
        <p class="comment" id="header_comment">comment</p>
    </header>
    <nav></nav>
    <hr>
    <main>
        <article>
            <section class="code_head">
                <h3 class="file" id="code_head_file">file</h3>
                <h4 class="change" id="code_head_change">change index</h4>

            </section>
            <section class="code_content" id="code_content">
                <table class="code" id="code_table">
                    <colgroup>
                        <col class="num">
                        <col class="status">
                        <col class="code">
                    </colgroup>
                    <!-- <tr class="code">
                        <td class="num">1</td>
                        <td class="status">+</td>
                        <td class="code increase">aaa</td>
                    </tr>
                    <tr class="code">
                        <td class="num">1000</td>
                        <td class="status">-</td>
                        <td class="code decrease">aaaa</td>
                    </tr> -->
                </table>
            </section>
        </article>
        <aside></aside>
    </main>
    <hr>
    <footer>
        <p id="powerby">power by patch view</p>
    </footer>
    <script>
        var modify_file = ''' + var + ''';

        function init(modify_file) {
            document.getElementById("header_title").innerText = modify_file.title;
            document.getElementById("header_time").innerText = modify_file.time;
            document.getElementById("header_comment").innerText = modify_file.comment;

            document.getElementById("code_head_file").innerText = modify_file.file;
            document.getElementById("code_head_change").innerText = modify_file.change;

            document.title = document.getElementById("header_title").innerText +
                " - " + document.getElementById("code_head_file").innerText;

        }
        init(modify_file);

        function add_sub(modify_file) {
            for (i in modify_file.content) {
                let sub = document.createElement("tr");
                sub.className = "code";

                let num = document.createElement("td");
                num.className = "num";
                num.innerText = parseInt(i)+1;

                let status = document.createElement("td");
                status.className = "status";
                if (modify_file.content[i][1] == 1) {
                    status.innerText = '+';
                } else if (modify_file.content[i][1] == 2) {
                    status.innerText = '-';
                } else {
                    status.innerText = ' ';
                }

                let code = document.createElement("td");
                if (modify_file.content[i][1] == 1) {
                    code.className = "code increase";
                } else if (modify_file.content[i][1] == 2) {
                    code.className = "code decrease";
                } else {
                    code.className = "code";
                }
                code.innerText = modify_file.content[i][0];

                sub.appendChild(num);
                sub.appendChild(status);
                sub.appendChild(code);
                document.getElementById("code_table").appendChild(sub);
            }
        }
        add_sub(modify_file);

    </script>
</body>

</html>
'''
    # print(html_text)
    html_file.write(html_text)
    del time
    del json


def init():
    parser = argparse.ArgumentParser(prog='patch_view.py', usage='%(prog)s [origin_file] [patch_file]',
                                     description='convert git patch to visual html or text')
    parser.add_argument('origin_file', help="origin file path")
    parser.add_argument('patch_file', help="git patch file path")
    parser.add_argument('-o', '--output', help="output file path")
    parser.add_argument(
        '-t', '--type', help="output type:\n  0 html\n  1 full text \n  2 new file\n  3 old file")

    args = parser.parse_args()
    print(args)
    return args


def main():

    # if len(argv) == 1:
    #     print('diff-view [origin_file] [diff_file]')
    #     return 0
    # if len(argv) < 3:
    #     print("need more args")
    #     return -1

    # origin_file = argv[1]
    # diff_file = argv[2]

    args = init()
    origin_file = args.origin_file
    diff_file = args.patch_file

    print("USE FILE\n    origin_file = {}\n    diff_file = {}\n".format(
        origin_file, diff_file))

    origin_file = open(origin_file, 'r')
    diff_file = open(diff_file, 'r')

    origin_text = origin_file.readlines()
    diff_text = diff_file.readlines()

    diff_header = find_diff_header(diff_text)
    atat = find_atat(diff_text, diff_header[0])

    modify_text = []

    modify_text = one_diff(origin_text, diff_text,
                           modify_text, atat, diff_header)
    # print(modify_text)

    # output_file(modify_text)
    # output_html(diff_header, diff_text, modify_text)
    if args.type == '0' or args.type == None:
        if args.output != None:
            output_html(diff_header, diff_text, modify_text, args.output)
        else:
            output_html(diff_header, diff_text, modify_text)
    elif args.type == '1':
        if args.output != None:
            output_file(modify_text, args.output, 0)
        else:
            output_file(modify_text, type_=0)
    elif args.type == '2':
        if args.output != None:
            output_file(modify_text, args.output, 1)
        else:
            output_file(modify_text, type_=1)
    elif args.type == '3':
        if args.output != None:
            output_file(modify_text, args.output, 2)
        else:
            output_file(modify_text, type_=2)
    else:
        print('unknow output type:', args.type)


if __name__ == "__main__":
    main()


# patch_view template html
'''
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <meta name='viewport' content='width=device-width initial-scale=1'>
    <title>patch view</title>
    <style>
        :root {
            font-size: 15px;
        }

        html {
            background-color: rgb(243, 243, 243);
        }

        body {
            margin: auto;
            padding: 1rem 1rem 1rem 1rem;
            max-width: 60rem;
        }

        header {
            padding: 0.1rem 1rem 0.1rem 1rem;
            border-radius: 0.5rem;
            background-color: rgba(191, 255, 191, 0.6);
        }

        article {
            padding: 0.1rem 1rem 1rem 1rem;
            border-radius: 0.5rem;
            background-color: rgba(255, 255, 255, 0.6);
        }

        section.code_head {
            border-radius: 0.1rem;
            background-color: rgb(243, 243, 243);
        }

        section.code_content {
            border-radius: 0.1rem;
            border: 1px solid rgb(201, 201, 201);
            overflow-x: auto;
        }

        table.code {
            width: 100%;
        }

        col.num {
            width: max-content;
            font-size: 1rem;
            color: rgb(60, 60, 60);
        }

        td.num {
            text-align: right;
            user-select:none;
        }

        col.status {
            width: max-content;
            text-align: center;
            font-size: 1rem;
            color: rgb(60, 60, 60);
        }

        td.status {
            text-align: center;
            background-color: rgb(201, 201, 201);
            user-select:none;
        }

        col.code {
            min-width: 80%;
        }

        td.increase {
            background-color: rgb(102, 245, 164);
        }

        td.decrease {
            background-color: rgb(252, 150, 150);
        }

        #powerby {
            text-align: center;
            color: rgb(60, 60, 60);
        }
    </style>
</head>

<body>
    <header>
        <h1 class="title" id="header_title">title</h1>
        <p class="time" id="header_time">time</p>
        <p class="comment" id="header_comment">comment</p>
    </header>
    <nav></nav>
    <hr>
    <main>
        <article>
            <section class="code_head">
                <h3 class="file" id="code_head_file">file</h3>
                <h4 class="change" id="code_head_change">change index</h4>

            </section>
            <section class="code_content" id="code_content">
                <table class="code" id="code_table">
                    <colgroup>
                        <col class="num">
                        <col class="status">
                        <col class="code">
                    </colgroup>
                    <!-- <tr class="code">
                        <td class="num">1</td>
                        <td class="status">+</td>
                        <td class="code increase">aaa</td>
                    </tr>
                    <tr class="code">
                        <td class="num">1000</td>
                        <td class="status">-</td>
                        <td class="code decrease">aaaa</td>
                    </tr> -->
                </table>
            </section>
        </article>
        <aside></aside>
    </main>
    <hr>
    <footer>
        <p id="powerby">power by diff view</p>
    </footer>
    <script>
        var modify_file = {
            "title": "title",
            "time": "time",
            "comment": "comment",
            "file": "file",
            "change": "change",
            "content": [["aa",0], ["aaaa",1], ["bbb",2]]
        };

        function init(modify_file) {
            document.getElementById("header_title").innerText = modify_file.title;
            document.getElementById("header_time").innerText = modify_file.time;
            document.getElementById("header_comment").innerText = modify_file.comment;

            document.getElementById("code_head_file").innerText = modify_file.file;
            document.getElementById("code_head_change").innerText = modify_file.change;

            document.title = document.getElementById("header_title").innerText +
                " - " + document.getElementById("code_head_file").innerText;

        }
        init(modify_file);

        function add_sub(modify_file) {
            for (i in modify_file.content) {
                let sub = document.createElement("tr");
                sub.className = "code";

                let num = document.createElement("td");
                num.className = "num";
                num.innerText = parseInt(i)+1;

                let status = document.createElement("td");
                status.className = "status";
                if (modify_file.content[i][1] == 1) {
                    status.innerText = '+';
                } else if (modify_file.content[i][1] == 2) {
                    status.innerText = '-';
                } else {
                    status.innerText = ' ';
                }

                let code = document.createElement("td");
                if (modify_file.content[i][1] == 1) {
                    code.className = "code increase";
                } else if (modify_file.content[i][1] == 2) {
                    code.className = "code decrease";
                } else {
                    code.className = "code";
                }
                code.innerText = modify_file.content[i][0];

                sub.appendChild(num);
                sub.appendChild(status);
                sub.appendChild(code);
                document.getElementById("code_table").appendChild(sub);
            }
        }
        add_sub(modify_file);

    </script>
</body>

</html>
'''
