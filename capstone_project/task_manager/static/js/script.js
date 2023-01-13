function getQuote() {
    $(document).ready(function () {
        let url = "https://type.fit/api/quotes";
        $.ajax({
            dataType: "json",
            url: url,
            success: function (data) {
                let index = Math.floor(Math.random() * data.length)
                content = data[index].text
                author = data[index].author
                author = author ? ` <i class="fa-solid fa-minus" style="margin:0 10px 0 10px"></i> ` + author : ``;           
                $("#author").html(author);
                $("#content").text(content);
            },
        });
    });
}