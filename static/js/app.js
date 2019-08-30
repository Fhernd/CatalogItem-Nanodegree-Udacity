debug = true;

$(document).ready(() => {
    checkAuthenticated();

    $.urlParam = function (name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)')
                          .exec(window.location.search);
    
        return (results !== null) ? results[1] || 0 : false;
    }

    if ($.urlParam('message')){
        alertify.alert('Message', $.urlParam('message'));
    }

    $('.delete').on('click', function (event) {
        event.preventDefault();

        var href = $(this).attr('href');

        alertify.confirm('Confirmation', 'Are you sure?', (e) => {
            if (e) {
                window.location = href;
            } else {
                return false;
            }
        }, () => { });
    });;

    $('#editItemModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var itemId = button.data('itemid');
        var title = button.data('title');
        var description = button.data('description');
        var categoryId = button.data('categoryid');

        var modal = $(this);
        modal.find('.modal-body #itemIdEdit').val(itemId);
        modal.find('.modal-body #titleEdit').val(title);
        modal.find('.modal-body #descriptionEdit').val(description);
        $(`#categoryIdEdit option[value='${categoryId}']`).prop('selected', true);
    });

    $('#viewItemModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var title = button.data('title');
        var description = button.data('description');
        var category = button.data('category');

        var modal = $(this);
        modal.find('.modal-body #titleView').val(title);
        modal.find('.modal-body #descriptionView').val(description);
        modal.find('.modal-body #categoryView').val(category);
    });
});

function logout() {
    printLog("Attempting logout...");

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/catalog/logout');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');

    xhr.onload = function () {
        printLog("Logging out the user");
        $('.result').html("Successfully logged out! Redirecting in 2 seconds...");
        setTimeout(function () {
            window.location.href = '/';
        }, 1000);
    }

    xhr.send('logout=true');
}


function onSignIn(googleUser) {
    printLog("Enter onSignIn()");

    var id_token = googleUser.getAuthResponse().id_token;

    var state = $('#state').data().state;

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/catalog/gconnect');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function () {
        var profile = googleUser.getBasicProfile();

        printLog('Signed in as: ' + profile.getName());

        var server_response = JSON.parse(xhr.responseText);

        // If data is true, it means that the user is authenticated and needs to refresh page
        if (server_response.data) {
            $('.result').html("Successfully logged in as " + profile.getName() + ". Redirecting in 4 seconds...");
            setTimeout(function () {
                window.location.href = "/";
            }, 1000);
        }
    };

    xhr.send('idtoken=' + id_token + '&state=' + state);
}

function checkAuthenticated() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/catalog/authenticated');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    xhr.onload = function () {
        var response = JSON.parse(xhr.responseText);

        printLog(response);
        if (response.data) {
            printLog("Logged in");
            showSignInBtn(false);
        } else {
            printLog("Not logged in");
            showSignInBtn(true);
        }
    }

    xhr.send();
}

function showSignInBtn(setVisible) {
    if (setVisible) {
        $('.google-auth, .facebook-auth').css('display', 'block');
        $('.sign-out').css('display', 'none');
    } else {
        $('.google-auth, .facebook-auth').css('display', 'none');
        $('.sign-out').css('display', 'block');
    }
}

function printLog(message) {
    if (debug) {
        console.log(message);
    }
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        printLog('User signed out.');
    });

    logout();
}

function logout() {
    printLog("Attempting logout...");

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/catalog/logout');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    
    xhr.onload = function () {
        printLog("Logging out the user");
        $('.result').html("Successfully logged out! Redirecting in 2 seconds...");
        setTimeout(function () {
            window.location.href = '/';
        }, 1000);
    }

    xhr.send('logout=true');
}
