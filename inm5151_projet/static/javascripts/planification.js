$(document).ready(function () {

    let currentPopoverContent = false;
    let currentSelectedEmploye = null;
    const cacheEmployeDisponibilites = {}

    function getSemaineChoisie() {
        return $('input[name=semaine-choisie]').val()
    }

    function getRowSelector(employe_id) {
        return $("#employe-" + employe_id);
    }

    function highLightDisponibilite(employe_id) {
        const dipsonibilites_vec = cacheEmployeDisponibilites[employe_id];
        const offset = getSemaineChoisie() == 2 ? 14 : 0;
        
        $("#employe-" + employe_id + " .cellule").each(function (i, _element) {
            if (dipsonibilites_vec[i + offset] == "1") {
                $(this).addClass("table-info");
            }
        });
    }

    $('html').on('click', function (e) {
        // Ce code a été pris sur:
        //https://stackoverflow.com/a/33953365
        let
            $popover,
            $target = $(e.target);

        //do nothing if there was a click on popover content
        if ($target.hasClass('popover') || $target.closest('.popover').length) {
            return;
        }

        $('[data-toggle="popover"]').each(function () {
            $popover = $(this);

            if (!$popover.is(e.target) &&
                $popover.has(e.target).length === 0 &&
                $('.popover').has(e.target).length === 0) {
                $popover.popover('hide');
            } else {
                //fixes issue described above
                //$popover.popover('toggle');
            }
        });
    });


    $(document).on('click', 'button.assignation', function (e) {
        e.preventDefault();
        horaire_id = $('input[name=horaire]').val();
        form = $('#form-disponibilites').serialize()
            .split('&')
            .map(function (str) {
                return parseInt(str.split('=')[1]);
            });
        let employe_id = form[0]
        let jour_id = form[1]
        let quart_to_activite = {};
        // Skip les deux premiers, car les deux premiers sont: employe_id et jour_id.
        for (let i = 2; i < form.length; i += 2) {
            if (!isNaN(form[i + 1])) {
                quart_to_activite[form[i]] = form[i + 1];
            } else {
                quart_to_activite[form[i]] = null
            }
        }
        csrftoken = getCookie('csrftoken');
        $.ajax({
            url: '/horaires/' + horaire_id,
            type: 'PUT',
            contentType: "text/json; charset=utf-8",
            data: JSON.stringify({
                quart_to_activite,
                employe_id,
                jour_id
            }),
            dataType: "html",
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function (response) {
                $('.cellule[data-employe-id=' + employe_id + '][data-cellule-id=' + jour_id + ']').html(response)
                $('[data-toggle="popover"]').popover('hide');
            },
            error: function (err) {
                console.log(err);
            }
        });
    });

    $(document).on('click', 'button.retirer-assignation', function (e) {
        e.preventDefault();
        horaire_id = $('input[name=horaire]').val();
        form = $('#form-disponibilites').serialize()
            .split('&')
            .map(function (str) {
                return parseInt(str.split('=')[1]);
            });
        let employe_id = form[0]
        let jour_id = form[1]
        csrftoken = getCookie('csrftoken');
        $.ajax({
            url: '/horaires/' + horaire_id + '/' + employe_id + '/' + jour_id,
            type: 'DELETE',
            contentType: "text/json; charset=utf-8",
            dataType: "html",
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function (response) {
                $('.cellule[data-employe-id=' + employe_id + '][data-cellule-id=' + jour_id + ']').html("")
                $('[data-toggle="popover"]').popover('hide');
            },
            error: function (err) {
                console.error(err);
            }
        });
    });

    $(document).on('DOMNodeInserted', function (e) {
        if ($(e.target).hasClass('popover')) {
            if (!currentPopoverContent) {
                $(e.target).popover('hide');
            }
        }
    })

    $("[data-toggle=popover]").popover({
        html: true,
        bottom: "auto",
        container: "body",
        content: function () {
            let employe_id = $(this).data("employe-id");
            let jour_id = $(this).data("cellule-id");
            let xhr = $.ajax({
                url: "/disponibilites?" + $.param({
                    employe_id,
                    jour_id
                }),
                dataType: "html",
                async: false
            });
            if (xhr.status == 200) {
                currentPopoverContent = true
                return xhr.responseText
            }
            currentPopoverContent = false;
        },
    });

    $(".cellule, .cellule-employe").hover(function () {
        const employe_id = $(this).data("employe-id");
        const horaire_id = $(this).data("horaire-id");
        const semaine_choisie = $(this).data("semaine_choisie")
        currentSelectedEmploye = employe_id
        if (cacheEmployeDisponibilites[employe_id] != null) {
            highLightDisponibilite(employe_id)
        } else {
            $.ajax({
                url: "/disponibilites/employe?" + $.param({
                    employe_id,
                    horaire_id,
                    semaine_choisie
                }),
                dataType: "json",
                success: function (dipsonibilites_vec) {
                    if(employe_id == currentSelectedEmploye) {
                        cacheEmployeDisponibilites[employe_id] = dipsonibilites_vec;
                        highLightDisponibilite(employe_id);
                    }
                }
            });
        }
    }, function () {
        getRowSelector(currentSelectedEmploye).find(".cellule").removeClass("table-info")
    })

});
