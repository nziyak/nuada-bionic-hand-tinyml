### KULLANICI:
iyi de modifiyesiz kart bizim projenin ne kadarını sağlayabilecek ki??@[/home/zia/Documents/school/graduation-project/nuada/nuada-bionic-hand-tinyml/docs/011126_notes.txt] ve buraya bugünkü sürecimizi yazmaya çalıştım unuttuğum bir şeyler var mı bakar mısın, ve senin sallen keyle ilgili yazmanı istediğim bi şeyleri de ekledim oraya ve madem böyle bir teorik durum vardı neden baştan ona göre söylemedin ki kapasitör değerlerini, sen dedin diye bu kapasitör değerlerini seçmiştik!!! senin yüzünden 500 tlmiz çöp oldu şu anda(internetten bir tanesi yaklaşık 500e geliyor, daha geçen gün kalan 3ünü satın aldım ve 1500 tl ödedim....), ve şu anki 50 hzlik salınımda kas kasılmaları az da olsa katkı sağlamıyor mu yani, 50 hzyi filtrelesek o kas kasılması kısmını alsak olmaz mı, ve emg aralığı neydi ekg aralığı neydi, ne kadarını kapsayacak ad8232 modifiyesiz hali
---

### KULLANICI:
bu envelope mevzularını, frekans aralıklarını falan da notlarımın sonlarına öğrenilenler olarak ekler misin, abartılı üsluptan kaçın, mütevazı olsun ve gereksiz türkçeye çeviri yapma terimleri olduğu gibi kullan. ve ayrıca envelope nedir ben anlamadım tam olarak ve madem yeterliydi biz niye modifiye ettik ki
---

### KULLANICI:
e peki mesela filtre katsayısı -'ye düşmeyecek şekilde seçseydik kapasitör değerlerini, o zaman ne olurdu? yine 50 hz girerdi 410a yükselttiğimiz için ama onu filtreleyebilir miydik bir şekilde? ve normalde 50 hzyi filtreleme yöntemleri yok mu böyle projelerde bizde neden olmuyor anlayamadım. ayrıca sen neden kapasitör değerlerini doğru vermedin ki? dokümanlara baktık diyorsun ama dokümanlarda bu kararsızlığa girme durumu da yazmıyor muydu
---

### KULLANICI:
bu yanlış değer önerme gerekçlerini de dosyaya yaz. neden yanlış değerleri seçtiğimizi justify edebilmeliyiz hocalara. ayrıca o zaman doğru değerlerde taksak düzgün çalışabilir mi diyorsun? şu anda orijinal mı taksak yoksa bu yeni değerlerde mi taksak bilemedim. ama çalışsa bile diğer 3ünü de modifye etmemiz gerekir. çalışmazsa da sadece onu orijinalleriyle değiştirmemiz gerekir. sanırım direkt orijinaliyle değiştirmek de yeterli olacak. hocalara olanları anlattıktan sonra deriz ki orijinalinin de semg envelopeu kapsadığını öğrenince bir daha kalan 3ünü modifiye etmeyelim dedik. ha bir de notumun başına da önce varsayımlarımız çalışıyor mu diye anlamak için modifiye edilmiş tek ad8232 ile deneme yaptığımı söyleyelim.
---

### KULLANICI:
e peki doğru kapasitörleri taksaydık bu sefer donanım osilasyona girmeyeceğinden 50 hz filtrlenemez miydi filtrelenebilirdi ki?? illa donanımsal notcha gerek olamzdı sanki o durumda yazılımsal da yapardık? ve son yaotığın dosyadaki değişikliklerde benim notlarımı da silmişsin ve abarıtlı ifadeler de kullanmışsın benim notlarımla uyumlu şekilde üslubuma da uyacak şekilde eklesene. ve en baştaki notu bu kadar resmi şekilde yazma mesela şunu yazsan yeter: low pass mod varsayımlarımızın doğruluğundan emin olmak için önce sadece bi kartı modidifye ettik ve şu anda onu deniyorum
---

### KULLANICI:
e peki doğru kapasitörleri taksaydık bu sefer donanım osilasyona girmeyeceğinden 50 hz filtrlenemez miydi filtrelenebilirdi ki?? illa donanımsal notcha gerek olamzdı sanki o durumda yazılımsal da yapardık? ve son yaotığın dosyadaki değişikliklerde benim notlarımı da silmişsin ve abarıtlı ifadeler de kullanmışsın benim notlarımla uyumlu şekilde üslubuma da uyacak şekilde eklesene. ve en baştaki notu bu kadar resmi şekilde yazma mesela şunu yazsan yeter: low pass mod varsayımlarımızın doğruluğundan emin olmak için önce sadece bi kartı modidifye ettik ve şu anda onu deniyorum ve sen bana 220 pf veya 150 pf demiştin 150 pf bualamadık diye öbürü olur dediğin için öbrünü kullandık 150 pf düşürmeyecekti eksiye
---

### KULLANICI:
açık kaynak projeler denememiş mi ki onların da aynı sorunu yaşamış olması lazım?
---

### KULLANICI:
bunları da notlarda uygun yere benim üslubumla ekler misin
---

### KULLANICI:
bunları da notlarda uygun yere benim üslubumla ekler misin, ama havadan konuşma öyle. "Arduino, Reddit ve yabancı biyomedikal maker forumlarında "AD8232 EMG mod yaptım, değerler gevşekken bile 0 ile 1023/4095 arasında deli gibi zıplıyor" diye açılmış onlarca başlık var." demiştin gerçek linkler bul yoksa halüsinasyon görmediğini nerden bileyim. "Pille Çalıştılar (Masaüstü Priz Döngüsünden Kaçtılar)
100 pF veya 150 pF takıp devreyi osilasyona sokmadan 400 Hz'e çıkaranların karşısına bu sefer analog 50 Hz şebeke gürültüsü çıktı.

Onlar sinyalin 0 V veya 3.3 V tavanına çarpıp kırpılmasını (clipping) engellemek için:
Devreyi prize takılı bir masaüstü bilgisayardan değil, tamamen pille/powerbank ile çalışan izole bir laptop veya mikrokontrolcü üzerinden beslediler.
Vücut ile elektrik şebekesi arasındaki ortak mod döngüsü (ground loop) pille kesilince 50 Hz gürültüsü küçüldü ve kırpılma olmadan yazılımsal filtre çalışabildi.
Bizim test ortamımızda ise sistem doğrudan prize takılı bilgisayar üzerinden beslendiği için 50 Hz ortamda çok daha yüksek bir genlikle bulunuyor." bunun için de aynısı geçerli
---

### KULLANICI:
"theremino.com/en/hardware/inputs/biometry-sensors#emg" linkini açtım sayfada bir tane bile 220 veya 150 sayısı geçmiyor. gerçek link istiyorum.
---

