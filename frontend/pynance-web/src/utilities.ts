export function containsObject(obj, list) {
    var i;
    for (i = 0; i < list.length; i++) {
        if (list[i] === obj) {
            return true;
        }
    }

    return false;
}

export function removeStringFromArray(element: string, array: string[]) {
    array.forEach((value,index)=>{
        if(value==element) array.splice(index,1);
    });
}