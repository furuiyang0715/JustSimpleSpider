var ret = function(input) {
        // 声明变量
        var keyStr = "ABCDEFGHIJKLMNOP" + "QRSTUVWXYZabcdef" + "ghijklmnopqrstuv"   + "wxyz0123456789+/" + "=";
        var output = "";
        var chr1, chr2, chr3 = "";
        var enc1, enc2, enc3, enc4 = "";
        var i = 0;

        do {
            // charCodeAt() 方法可返回指定位置的字符的Unicode 编码
            chr1 = input.charCodeAt(i++);
            console.log("i is " + i, "chr1 is " + chr1)
            chr2 = input.charCodeAt(i++);
            // 当超出索引的时候 chr2 为 NaN
            console.log("i is " + i, "chr2 is " + chr2)
            // 同理这时 chr3 也是 NaN
            chr3 = input.charCodeAt(i++);
            console.log("i is " + i, "chr3 is " + chr3)

            enc1 = chr1 >> 2;
            // enc1 是正常值 chr1(57) 计算出来的 14
            console.log("chr1 is " + chr1, "enc1 is " + enc1)
            // enc2 是 16 这时相当于只计算 ((chr1 & 3) << 4)
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
            console.log("chr1 is " + chr1, "chr2 is " + chr2, "enc2 is " + enc2)
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
            console.log("chr2 is " + chr1, "chr3 is " + chr2, "enc3 is " + enc2)
            enc4 = chr3 & 63;
            console.log("chr3 is " + chr2, "enc4 is " + enc2)

            console.log("=======================")

            console.log(chr1, chr2, chr3, enc1, enc2, enc3, enc4);
            // 57 NaN NaN 14 16 0 0

            // isNaN() 函数用于检查其参数是否是非数字值。
            if (isNaN(chr2)) {
                enc3 = enc4 = 64;
            } else if (isNaN(chr3)) {
                enc4 = 64;
            }
            // charAt() 方法从一个字符串中返回指定的字符
            output = output + keyStr.charAt(enc1) + keyStr.charAt(enc2) + keyStr.charAt(enc3) + keyStr.charAt(enc4);
            chr1 = chr2 = chr3 = "";
            enc1 = enc2 = enc3 = enc4 = "";
        } while (i < input.length);

        return output;
    }

var input = '1581996129'   // 时间戳字符串


ret(input)


// 运行: node test.js
