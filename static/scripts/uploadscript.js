$(function () {
  $(document).on("change", ".uploadFile", function () {
    var uploadFile = $(this);
    var files = !!this.files ? this.files : [];
    if (!files.length || !window.FileReader) return; // dosya seçilmedi veya FileReader desteği yok

    if (/^image/.test(files[0].type)) {
      // sadece resim dosyaları
      var reader = new FileReader();
      reader.readAsDataURL(files[0]); // dosyayı oku

      reader.onloadend = function () {
        uploadFile
          .closest(".imgUp")
          .find(".imagePreview")
          .css("background-image", "url(" + this.result + ")");
      };
    }
  });
});
