export function containsObject(obj, list) {
    var i;
    for (i = 0; i < list.length; i++) {
        if (list[i] === obj) {
            return true;
        }
    }
    return false;
}

export function uniqueArray(arr){
    return arr.filter(function (value, index, self) {
        return self.indexOf(value) === index;
    });
}

// YYYY-MM-DD
export function dateToString(date: Date) : string{
    let year = date.getFullYear();
    let month = date.getMonth() + 1;
    let day = date.getDate();

    let month_string : string;
    if(month<10){ month_string = "0".concat(`${month}`); }
    else{ month_string = `${month}`};

    let day_string: string;
    if(day<10) { day_string = "0".concat(`${day}`)}
    else{ day_string = `${day}`};

    let full_date_string = `${year}-${month_string}-${day_string}`;
    return full_date_string;
}

export function getColumnFromList(column_name, list ){
    let parsed_list = []
    for(let entry of list){ parsed_list.push(entry[column_name]) }
    return parsed_list;
}

export function logAllObjectProperties(thisObject: Object): void{
    Object.keys(thisObject).forEach((prop)=> console.log(prop));
}

export function arraysEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (a.length !== b.length) return false;
  
    for (var i = 0; i < a.length; ++i) {
      if (a[i] !== b[i]) return false;
    }
    return true;
  }