export function containsObject(obj, list) {
    var i;
    for (i = 0; i < list.length; i++) {
        if (list[i] === obj) {
            return true;
        }
    }

    return false;
}

// YYYY-MM-DD
export function dateToString(date: Date) : string{
    let year = date.getUTCFullYear();
    let month = date.getUTCMonth();
    let day = date.getDay();

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