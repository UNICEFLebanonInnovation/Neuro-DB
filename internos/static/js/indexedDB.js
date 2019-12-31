/**
 * Created by Ali on 2016-08-26.
 */

var db = null;

function createDataStore(database_name, version,  store_name, create_default_item, callback)
{
    var request = indexedDB.open(database_name, version);

    request.onupgradeneeded = function() {
        // The database did not previously exist, so create object stores and indexes.
        db = request.result;
        var flag = false;
        try {
            if(!db.objectStoreNames().contains(store_name)) {
                flag = true;
            }
        }catch(err) {
            flag = true;
        }
        if(flag){
            db.createObjectStore(store_name, {keyPath: "id", autoIncrement:true});
            var store1 = db.createObjectStore("schools", {keyPath: "id", autoIncrement:true});
            store1.createIndex('location', 'location', { unique: false, multiEntry: true });
        }
    };

    request.onsuccess = function() {
        db = request.result;
        if(create_default_item){
            create_default_values(store_name);
        }
        if(callback){
            callback();
        }
    };
}

function create_default_values(store_name)
{
    var store = getStoreByName(store_name);
    var item = {synchronized: false, deleted: false, completed: false, pending: true};
    item = collect_form_values($('#mainForm'), item);

    var request = store.put(item);
    request.onsuccess = function(){
        var result = request.result;
        $("#main_id").val(result);
    };
}

function collect_form_values(form, item)
{
    $(form.find('input')).each(function(i, field){
        item[$(field).attr('name')] = $(field).val();
    });

    $(form.find('select')).each(function(i, field){
        item[$(field).attr('name')] = $(field).val();
    });

    $(form.find('textarea')).each(function(i, field){
        item[$(field).attr('name')] = $(field).val();
    });

    return item;
}

function add_item(item, store_name){
    var store = getStoreByName(store_name);
    store.add(item);
}

function update_form_values(form, item)
{
    $(form.find('input')).each(function(i, field){
        $(field).val(item[$(field).attr('name')]);
    });

    $(form.find('select')).each(function(i, field){
        updateDropDownValue($(field),item[$(field).attr('name')]);
    });

    $(form.find('textarea')).each(function(i, field){
         $(field).val(item[$(field).attr('name')]);
    });

    return item;
}

function append_item_store(itemid, name, value, store_name, callback)
{
    var store = getStoreByName(store_name);
    var request = store.get(itemid);
    request.onsuccess = function(){
        var result = request.result;
        var item = result[name];
        if(item == undefined){
            item = [];
        }
        var index = item.push(value);
        result[name] = item;
        store.put(result);
        if(callback != undefined){
            callback(index);
        }
    };
}

function delete_subitem_store(itemid, name, index, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.get(itemid);
    request.onsuccess = function(){
        var result = request.result;
        var subitems = result[name];
        subitems.splice(parseInt(index)-1, 1);
        result[name] = subitems;
        store.put(result);
    };
}

function update_subitem_store(itemid, name, index, store_name, newValue)
{
    var store = getStoreByName(store_name);
    var request = store.get(itemid);
    request.onsuccess = function(){
        var result = request.result;
        var subitems = result[name];
        subitems[parseInt(index)-1] = newValue;
        result[name] = subitems;
        store.put(result);
    };
}

function get_subitem_store(itemid, name, index, store_name, callback)
{
    var store = getStoreByName(store_name);
    var request = store.get(itemid);
    request.onsuccess = function(){
        var result = request.result;
        var subitems = result[name];
        callback(subitems[parseInt(index)-1]);
    };
}

function getStoreByName(name)
{
    var store = db.transaction([name], "readwrite").objectStore(name);
    return store;
}

function getRecord(itemid, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.get(parseInt(itemid));
    return request;
}

function update_item_store(itemid, name, value, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.get(itemid);
    request.onsuccess = function(){
        var item = request.result;
        item[name] = value;
        store.put(item);
    };
}

function flag_record_to_update(itemid, store_name)
{
    update_item_store(itemid, 'to_update', true, store_name);
}

function update_or_create_item(itemid, name, value, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.get(itemid);
    request.onsuccess = function(){
        var item = request.result;
        if(item){
            item[name] = value;
        }else{
            var item = {id: itemid};
            item[name] = value;
        }
        store.put(item);
    };
}

function update_one_by_index(index_name, index_value, name, value, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.index(index_name).get(index_value);

    request.onsuccess = function(){
        var item = request.result;
        if(item){
            item[name] = value;
            store.put(item);
        }
    };
}

function update_items_by_index(index_name, index_value, name, value, store_name)
{
    var store = getStoreByName(store_name);
    var request = store.index(index_name).getAll(index_value);
    request.onsuccess = function(){
        var result = request.result;
        if(result){
            $(result).each(function(i, item){
                item[name] = value;
                store.put(item);
            });
        }
    };
}

function delete_from_store(itemid, store_name, force_delete)
{
    var store = getStoreByName(store_name);
    var request = store.get(parseInt(itemid));
    request.onsuccess = function(){
        result = request.result;
        if(force_delete == true){
            store.delete(parseInt(itemid));
        }else if(result.synchronized == true){
            update_item_store(parseInt(itemid), 'deleted', true, store_name);
        }else{
            store.delete(parseInt(itemid));
        }
    }
}
