import json
import pprint

import requests as req
url = "http://webapi.cninfo.com.cn//api/sysapi/p_sysapi1128"
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'http://webapi.cninfo.com.cn/',
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    # 'Cookie': '__qc_wId=726; pgv_pvid=6020356972; Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b=1581945588; '
    #           'codeKey=02e5be195b; Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b=1581945773',
    # __qc_wId=726; pgv_pvid=6020356972; Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b=1581945588;
    # codeKey=a46215bf5e; Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b=1581946570
    'Origin': 'http://webapi.cninfo.com.cn',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Content-Length': '0',
    'Host': 'webapi.cninfo.com.cn',
    # 'mcode': 'MTU4MTk0NTc3Mg==',
    # 'mcode': 'MTU4MTk0NjU3MA==',
    'mcode': 'MTU4MTk0NzQzOQ==',
    'Pragma': 'no-cache',
    'X-Requested-With': 'XMLHttpRequest'

}
ret = req.post(url, headers=headers).text
py_data = json.loads(ret)
print(pprint.pformat(py_data))


"""
headers: {"mcode": indexcode.getResCode()},

var indexcode={
    getResCode:function(){
        var time=Math.floor(new Date().getTime()/1000);
        return window.JSonToCSV.missjson(""+time);
    }
}

var JSonToCSV = {
    /*
     * obj是一个对象，其中包含有：
     * ## data 是导出的具体数据
     * ## fileName 是导出时保存的文件名称 是string格式
     * ## showLabel 表示是否显示表头 默认显示 是布尔格式
     * ## columns 是表头对象，且title和key必须一一对应，包含有
          title:[], // 表头展示的文字
          key:[], // 获取数据的Key
          formatter: function() // 自定义设置当前数据的 传入(key, value)
     */
    setDataConver: function(obj) {
        var bw = this.browser();
        if(bw['ie'] < 9) return; // IE9以下的
        var data = obj['data'],
            ShowLabel = typeof obj['showLabel'] === 'undefined' ? true : obj['showLabel'],//是否显示标题
            fileName = (obj['fileName'] || 'UserExport') + '.csv',
            columns = obj['columns'] || {
                title: [],
                key: [],
                formatter: undefined
            };
        var ShowLabel = typeof ShowLabel === 'undefined' ? true : ShowLabel;
        var row = "", CSV = '', key;
        // 如果要现实表头文字
        if (ShowLabel) {
            // 如果有传入自定义的表头文字
            if (columns.title.length) {
                columns.title.map(function(n) {
                    row += n + ',';
                });
            } else {
                // 如果没有，就直接取数据第一条的对象的属性
                for (key in data[0]) row += key + ',';
            }
            row = row.slice(0, -1); // 删除最后一个,号，即a,b, => a,b
            CSV += row + '\r\n'; // 添加换行符号
        }
        // 具体的数据处理
        data.map(function(n) {
            row = '';
            // 如果存在自定义key值
            if (columns.key.length) {
                columns.key.map(function(m) {
                    row += '"' + (typeof columns.formatter === 'function' ? columns.formatter(m, n[m]) : n[m]) + '",';
                });
            } else {
                for (key in n) {
                    row += '"' + (typeof columns.formatter === 'function' ? columns.formatter(key, n[key]) : n[key]) + '",';
                }
            }
            row.slice(0, row.length - 1); // 删除最后一个,
            CSV += row + '\r\n'; // 添加换行符号
        });
        if(!CSV) return;
        this.SaveAs(fileName, CSV); //自动下载
    },
    SaveAs: function(fileName, csvData) {
        var bw = this.browser();
        if(!bw['edge'] && !bw['ie']) {
            var alink = document.createElement("a");
            alink.id = "linkDwnldLink";
            alink.href = this.getDownloadUrl(csvData);
            document.body.appendChild(alink);
            var linkDom = document.getElementById('linkDwnldLink');
            linkDom.setAttribute('download', fileName);
            linkDom.click();
            document.body.removeChild(linkDom);
        }
        else if(bw['ie'] >= 10 || bw['edge'] == 'edge') {
            var _utf = "\uFEFF";
            var _csvData = new Blob([_utf + csvData], {
                type: 'text/csv'
            });
            window.navigator.msSaveBlob(_csvData, fileName);
        }
        else {
            var oWin = window.top.open("about:blank", "_blank");
            oWin.document.write('sep=,\r\n' + csvData);
            oWin.document.close();
            oWin.document.execCommand('SaveAs', true, fileName);
            oWin.close();
        }
    },
    getDownloadUrl: function(csvData) {
        var _utf = "\uFEFF"; // 为了使Excel以utf-8的编码模式，同时也是解决中文乱码的问题
        if (window.Blob && window.URL && window.URL.createObjectURL) {
            var csvData = new Blob([_utf + csvData], {
                type: 'text/csv'
            });
            return URL.createObjectURL(csvData);
        }
        // return 'data:attachment/csv;charset=utf-8,' + _utf + encodeURIComponent(csvData);
    },
    browser: function() {
        var Sys = {};
        var ua = navigator.userAgent.toLowerCase();
        var s;
        (s = ua.indexOf('edge') !== - 1 ? Sys.edge = 'edge' : ua.match(/rv:([\d.]+)\) like gecko/)) ? Sys.ie = s[1]:
            (s = ua.match(/msie ([\d.]+)/)) ? Sys.ie = s[1] :
                (s = ua.match(/firefox\/([\d.]+)/)) ? Sys.firefox = s[1] :
                    (s = ua.match(/chrome\/([\d.]+)/)) ? Sys.chrome = s[1] :
                        (s = ua.match(/opera.([\d.]+)/)) ? Sys.opera = s[1] :
                            (s = ua.match(/version\/([\d.]+).*safari/)) ? Sys.safari = s[1] : 0;
        return Sys;
    },		
      
    missjson:function(input) {  
        var keyStr = "ABCDEFGHIJKLMNOP" + "QRSTUVWXYZabcdef" + "ghijklmnopqrstuv"   + "wxyz0123456789+/" + "=";  
        var output = "";  
        var chr1, chr2, chr3 = "";  
        var enc1, enc2, enc3, enc4 = "";  
        var i = 0;  
        do {  
            chr1 = input.charCodeAt(i++);  
            chr2 = input.charCodeAt(i++);  
            chr3 = input.charCodeAt(i++);  
            enc1 = chr1 >> 2;  
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);  
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);  
            enc4 = chr3 & 63;  
            if (isNaN(chr2)) {  
                enc3 = enc4 = 64;  
            } else if (isNaN(chr3)) {  
                enc4 = 64;  
            }  
            output = output + keyStr.charAt(enc1) + keyStr.charAt(enc2)  
                    + keyStr.charAt(enc3) + keyStr.charAt(enc4);  
            chr1 = chr2 = chr3 = "";  
            enc1 = enc2 = enc3 = enc4 = "";  
        } while (i < input.length);  
  
        return output;  
    }  
};
window.JSonToCSV = JSonToCSV;


"""
