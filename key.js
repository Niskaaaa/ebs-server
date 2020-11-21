var origin = {red_apple:'111',blue_apple:{   green_apple:{    orange_apple:'222'   }  } }

function deepCopy(newObj,oldObj){

    for (x in oldObj)
    if(typeof(x)===Array){
        var newSub=[]
        deepCopy(newSub,x)
    }
    else if (typeof(x)==Object){
        var newSub = {}
        deepCopy(newSub,x)
    }
    else newObj = oldObj

    return newObj
}