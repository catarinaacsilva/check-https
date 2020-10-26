function json2table(json, classes, threshold) {
    var cols = ['date', 'https', 'certificate', 'http_redirect', 'http_r301', 'hsts', 'https_redirect', 'https_r301', 'similarity'];
    var qualities = ['https', 'certificate', 'http_redirect', 'http_r301', 'hsts']
    var defects = ['https_redirect', 'https_r301']
    var headerRow = '';
    var bodyRows = '';


    classes = classes || '';
    threshold = threshold || .9;

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    cols.map(function (col) {
        headerRow += '<th>' + capitalizeFirstLetter(col) + '</th>';
    });

    json.map(function (row) {
        bodyRows += '<tr>';

        cols.map(function (colName) {
            if (qualities.includes(colName)) {
                var value = row[colName]
                if (value) {
                    bodyRows += '<td> <font color="#98971a">' + row[colName] + '</font> </td>';
                } else {
                    bodyRows += '<td> <font color="#cc241d">' + row[colName] + '</font> </td>';
                }
            } else if (defects.includes(colName)) {
                var value = row[colName]
                if (value) {
                    bodyRows += '<td> <font color="#cc241d">' + row[colName] + '</font> </td>';
                } else {
                    bodyRows += '<td> <font color="#98971a">' + row[colName] + '</font> </td>';
                }
            } else if (colName == 'similarity') {
                var value = parseFloat(row[colName]);
                if (value >= threshold) {
                    bodyRows += '<td> <font color="#98971a">' + row[colName] + '</font> </td>';
                } else {
                    bodyRows += '<td> <font color="#cc241d">' + row[colName] + '</font> </td>';
                }
            } else {
                bodyRows += '<td>' + new Date(row[colName]).toISOString().split('T')[0] + '</td>';
            }
        })

        bodyRows += '</tr>';
    });

    return '<table class="' +
        classes +
        '"><thead><tr>' +
        headerRow +
        '</tr></thead><tbody>' +
        bodyRows +
        '</tbody></table>';
}

function test() {
    var select = document.getElementById('municipality_name');
    if (select.selectedIndex > 0) {
        var name = select.options[select.selectedIndex].value;
        var request = new XMLHttpRequest();
        console.log('https://hrun.hopto.org/https/api/tests?name=' + name);
        request.open('GET', 'https://hrun.hopto.org/https/api/tests?name=' + name, true);
        request.onload = function () {
            if (request.status >= 200 && request.status < 400) {
                var data = JSON.parse(this.response);
                document.getElementById('table').innerHTML = json2table(data['tests'], 'table');
            } else {
                console.log('Error - unable to load the municipality evaluation...')
            }
        }
        request.send();
    }
}


function load() {
    var request = new XMLHttpRequest()
    console.log('https://hrun.hopto.org/https/api/municipality');
    request.open('GET', 'https://hrun.hopto.org/https/api/municipality', true);
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            var data = JSON.parse(this.response)
            var select = document.getElementById('municipality_name');
            var options = data['municipality'];

            for (var i = 0; i < options.length; i++) {
                var opt = options[i];
                var el = document.createElement("option");
                el.textContent = opt;
                el.value = opt;
                select.appendChild(el);
            }
            select.onchange = test;
        } else {
            console.log('Error - unable to load the municipality names...');
        }
    }
    request.send();
}

window.onload = load;