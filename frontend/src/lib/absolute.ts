export let getAbsoluteUrl = (function() {
    var a: HTMLAnchorElement;
    return function(url: string) {
        if (!a) a = document.createElement('a');
        a.href = url;
        return a.href;
    };
})();
