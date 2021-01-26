import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX


def templateMatching(img, template, path, value=0):
    # Ana resmi oku
    img_rgb = cv2.imread(img)

    # Gri tonlamaya dönüştür
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    # 0 parametresi resmi gri tonlama modunda okumak için
    template = cv2.imread(template, 0)

    # Şablonun genişliğini ve yüksekliğini w ve h olarak tut
    w, h = template.shape[::-1]

    # Eşleşme işlemini gerçekleştir.
    # Kullanılan Algoritma: Normalleştirilmiş Çapraz Korelasyon (Normalized Cross-Correlation)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

    # En iyi eşleşmeyi bul
    if value == 0:
        for threshold in np.arange(1, 0.1, -0.01):
            if (res >= threshold).any():
                loc = np.where(res >= threshold)
                value = int(round(threshold * 100))
                break
    else:  # Kullanıcının belirlediği eşik değerine göre sonucu bul
        loc = np.where(res >= int(value) / 100)

    a = np.unique(loc[0], axis=0)
    b = np.unique(loc[1], axis=0)
    c = np.array((a, b))

    pt0 = 0
    pt1 = 0
    # Eşlenen alanda bir dikdörtgen çizdir
    # Sentaks: cv2.rectangle(resim, başlangıç_noktası, bitiş_noktası, renk, kalınlık)
    for pt in zip(*c[::-1]):
        if abs(pt0 - pt[0]) < 3 and abs(pt1 - pt[1]) < 3:
            pt0 = pt[0]
            pt1 = pt[1]
            continue
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (124, 252, 0), 2)
        cv2.putText(img_rgb, "%" + str(value),
                    (pt[0] + w, pt[1] + h), font, 1, (124, 252, 0), 2)
        pt0 = pt[0]
        pt1 = pt[1]
    # Şablon eşleşme sonucunu parametre ile gelen dosya yoluna kaydet
    cv2.imwrite(path, img_rgb)

    return value
