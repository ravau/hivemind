#!/usr/bin/env python3
import os
import csv
import requests
import json
from time import perf_counter


def process_file_name(file_name, tavern_root_dir):
    return file_name.replace(tavern_root_dir, "").lstrip("/")

def get_requests_from_yaml(tavern_root_dir):
    from fnmatch import fnmatch
    import yaml
    from json import dumps
    ret = {}
    pattern = "*.tavern.yaml"
    for path, subdirs, files in os.walk(tavern_root_dir):
        for name in files:
            if fnmatch(name, pattern):
                test_file = os.path.join(path, name)
                yaml_document = None
                with open(test_file, "r") as yaml_file:
                    yaml_document = yaml.load(yaml_file, Loader=yaml.BaseLoader)
                if "stages" in yaml_document:
                    if "request" in yaml_document["stages"][0]:
                        json_parameters = yaml_document["stages"][0]["request"].get("json", None)
                        assert json_parameters is not None, "Unable to find json parameters in request"
                        ret[process_file_name(test_file, tavern_root_dir)] = dumps(json_parameters)
    return ret

def abs_rel_diff(a, b):
    return abs((a - b) / float(b)) * 100.

def parse_csv_files(root_dir):
    ret = {}
    file_path = os.path.join(root_dir, "benchmark.csv")
    print("Processing file: {}".format(file_path))
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            test_name = row[0] + ".tavern.yaml"
            test_time = float(row[1])
            if test_name in ret:
                ret[test_name].append(test_time)
            else:
                ret[test_name] = [test_time]
    return ret

if __name__ == "__main__":
    import argparse
    from statistics import mean, median

    parser = argparse.ArgumentParser()
    parser.add_argument("address", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("csv_report_dir", type=str, help="Path to benchmark csv reports")
    parser.add_argument("tavern_root_dir", type=str, help="Path to tavern tests root dir")
    parser.add_argument("--median-cutoff-time", dest="cutoff_time", type=float, default=0.3, help="Tests with median time below cutoff will not be shown")
    parser.add_argument("--time-threshold", dest="time_threshold", type=float, default=1.0, help="Time threshold for test execution time, tests with execution time greater than threshold will be marked on red.")
    args = parser.parse_args()

    assert os.path.exists(args.csv_report_dir), "Please provide valid csv report path"
    assert os.path.exists(args.tavern_root_dir), "Please provide valid tavern path"

    report_data = parse_csv_files(args.csv_report_dir)
    request_data = get_requests_from_yaml(args.tavern_root_dir)

    html_file = "tavern_benchmarks_report.html"
    above_treshold = []
    with open(html_file, "w") as ofile:
        ofile.write("<html>\n")
        ofile.write("  <head>\n")
        ofile.write("  <meta charset=\"UTF-8\">\n")
        ofile.write("    <style>\n")
        ofile.write("      table, th, td {\n")
        ofile.write("        border: 1px solid black;\n")
        ofile.write("        border-collapse: collapse;\n")
        ofile.write("      }\n")
        ofile.write("      th, td {\n")
        ofile.write("        padding: 15px;\n")
        ofile.write("      }\n")
        ofile.write("    </style>\n")
        ofile.write("    <link rel=\"stylesheet\" type=\"text/css\" href=\"https://cdn.datatables.net/1.10.22/css/jquery.dataTables.css\">\n")
        ofile.write("    <script src=\"https://code.jquery.com/jquery-3.5.1.js\" integrity=\"sha256-QWo7LDvxbWT2tbbQ97B53yJnYU3WhH/C8ycbRAkjPDc=\" crossorigin=\"anonymous\"></script>\n")
        ofile.write("    <script type=\"text/javascript\" charset=\"utf8\" src=\"https://cdn.datatables.net/1.10.22/js/jquery.dataTables.js\"></script>\n")
        ofile.write("    <script type=\"text/javascript\" charset=\"utf8\">\n")
        ofile.write("      $(document).ready( function () {\n")
        ofile.write("        $('#benchmarks').DataTable({\"aLengthMenu\": [[10, 25, 50, 100, 1000, 10000, -1], [10, 25, 50, 100, 1000, 10000, \"All\"]]});\n")
        ofile.write("      } );\n")
        ofile.write("    </script>\n")
        ofile.write("    <script src=\"https://polyfill.io/v3/polyfill.min.js?features=es6\"></script>\n")
        ofile.write("    <script id=\"MathJax-script\" async src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js\"></script>\n")
        ofile.write("  </head>\n")
        ofile.write("  <body>\n")
        ofile.write("    <table id=\"benchmarks\">\n")
        ofile.write("      <thead>\n")
        ofile.write("        <tr><th>Test name</th><th>Min time [ms]</th><th>Max time [ms]</th><th>Mean time [ms]</th><th>Median time [ms]</th><th>Reference (pure requests call) [ms]</th><th>\[ {\\vert} {T_{mean} - T_{ref} \over T_{ref}} {\lvert} \cdot 100 \] [%]</th><th>\[ {\\vert} {T_{median} - T_{ref} \over T_{ref}} {\lvert} \cdot 100 \] [%]</th></tr>\n")
        ofile.write("      </thead>\n")
        ofile.write("      <tbody>\n")
        for name, data in report_data.items():
            dmin = min(data)
            dmax = max(data)
            dmean = mean(data)
            dmedian = median(data)
            if dmedian >= args.cutoff_time:
                t_start = perf_counter()
                ret = requests.post("{}:{}".format(args.address, args.port), request_data[name])
                if ret.status_code == 200:
                    ref_time = perf_counter() - t_start
                else:
                    ref_time = 0.
                if dmean > args.time_threshold:
                    ofile.write("        <tr><td>{}<br/>Parameters: {}</td><td>{:.4f}</td><td>{:.4f}</td><td bgcolor=\"red\">{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td></tr>\n".format(name, request_data[name], dmin * 1000, dmax * 1000, dmean * 1000, dmedian * 1000, ref_time * 1000, abs_rel_diff(dmean, ref_time), abs_rel_diff(dmedian, ref_time)))
                    above_treshold.append((name, "{:.4f}".format(dmean), request_data[name]))
                else:
                    ofile.write("        <tr><td>{}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td></tr>\n".format(name, dmin * 1000, dmax * 1000, dmean * 1000, dmedian * 1000, ref_time * 1000, abs_rel_diff(dmean, ref_time), abs_rel_diff(dmedian, ref_time)))
        ofile.write("      </tbody>\n")
        ofile.write("    </table>\n")
        ofile.write("  </body>\n")
        ofile.write("</html>\n")

    if above_treshold:
        from prettytable import PrettyTable
        summary = PrettyTable()
        print("########## Test failed with following tests above {}s threshold ##########".format(args.time_threshold * 1000))
        summary.field_names = ['Test name', 'Mean time [ms]', 'Call parameters']
        for entry in above_treshold:
            summary.add_row(entry)
        print(summary)
        exit(2)
    exit(0)
