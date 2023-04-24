function createLogElement(title, time, message) {
    // Create a new log message element with jQuery
    const logElem = $('<div></div>').addClass('bg-white overflow-hidden shadow sm:rounded-lg relative');
    const contentElem = $('<div></div>').addClass('px-4 py-5 sm:p-6 flex items-center').appendTo(logElem);
    const titleElem = $('<div></div>').addClass('flex items-center justify-between').appendTo(contentElem);
    const titleTextElem = $('<h3></h3>').addClass('text-lg font-medium text-gray-900').html(title+':&nbsp;&nbsp;').appendTo(titleElem);
    const messageElem = $('<div></div>').addClass('mt-4').appendTo(contentElem);
    const messageTextElem = $('<p></p>').addClass('text-sm text-gray-500').html(message).appendTo(titleElem);
    const timeElem = $('<p></p>').addClass('text-sm font-medium text-gray-500 ml-auto').text(time).appendTo(contentElem);
    const dividerElem = $('<hr>').addClass('border-t border-gray-200').appendTo(logElem);

    // Return the log message element
    return logElem;
}