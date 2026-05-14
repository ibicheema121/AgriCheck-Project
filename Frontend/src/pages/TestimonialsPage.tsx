import { StaticPageLayout } from "@/components/StaticPageLayout";
import { Star, Quote } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function TestimonialsPage() {
  const { language } = useLanguage();
  const isUrdu = language === "ur";

  const testimonials = isUrdu ? [
    {
      name: "محمود نواز شاہ",
      role: "جی ڈیلائٹ فارم، سندھ",
      text: "ہم ایک سال سے زیادہ عرصے سے ایگری چیک کی خدمات استعمال کر رہے ہیں۔ ہم فیلڈ سے ریئل ٹائم قابل اعتماد معلومات حاصل کرنے پر بہت خوش ہیں۔ پاکستان میں یہ ٹیکنالوجی ترقی دینا اور اسے فیلڈ میں قابل عمل بنانا ایک چیلنج ہے۔ ہم امید کرتے ہیں کہ آم اور کیلے سے آگے اپنے کام کو جاری اور وسیع کریں گے۔",
      rating: 5,
    },
    {
      name: "احمد خان",
      role: "گندم کاشتکار، پنجاب",
      text: "ایگری چیک نے میرے کھیتوں کے انتظام کا طریقہ بدل دیا۔ صرف ریئل ٹائم NPK ڈیٹا نے مجھے گزشتہ سیزن میں کھاد کے اخراجات میں 20٪ کی بچت کی۔ سینسر پروبز درست زیر زمین ریڈنگز دیتے ہیں جو مجھے بہتر آبپاشی فیصلے کرنے میں مدد کرتے ہیں۔",
      rating: 5,
    },
    {
      name: "فاطمہ بی بی",
      role: "سبزی اگانے والی، سندھ",
      text: "AI مشیر اردو بولتا ہے  یہ میرے لیے گیم چینجر تھا۔ مجھے فصل کی سفارشات ملتی ہیں جن کو میں واقعی سمجھ سکتی ہوں اور ان پر عمل کر سکتی ہوں۔ ماہرین زراعت کی ہفتہ وار رپورٹس پورے بڑھتے ہوئے موسم میں مجھے ٹریک پر رکھتی ہیں۔",
      rating: 5,
    },
    {
      name: "راشد علی",
      role: "چاول کاشتکار، KPK",
      text: "میں نے اپنے دھان کے کھیتوں میں سینسرز نصب کیے۔ مٹی کے ڈیٹا کے ساتھ مل کر سیٹلائٹ امیجری نے مجھے نکاسی کے مسائل شناخت کرنے میں مدد کی جنہیں میں سالوں سے نظرانداز کر رہا تھا۔ ایک سیزن میں میرا پانی کا استعمال 35٪ کم ہو گیا۔",
      rating: 4,
    },
    {
      name: "طارق محمود",
      role: "گنے کا کاشتکار، ملتان",
      text: "مٹی کے درجہ حرارت اور نمی کی نگرانی نے مجھے اپنے آبپاشی کے شیڈول کو بہتر بنانے میں مدد کی۔ کیڑوں کی پیش گوئی کی خصوصیت نے میری فصل کو ایک بڑے حملے سے بچایا۔ ایک سیزن میں میری پیداوار 25٪ بڑھ گئی۔",
      rating: 5,
    },
    {
      name: "نادیہ حسین",
      role: "نامیاتی فارم مالک، اسلام آباد",
      text: "آخر کار، ایک ایسا پلیٹ فارم ملا جو مجھے پیچیدگی کے بغیر درکار ڈیٹا دیتا ہے۔ سیٹ اپ آسان تھا اور سپورٹ بہت اچھی رہی ہے۔ ان کے ماہرین زراعت کے ماہانہ فیلڈ وزٹس انتہائی قیمتی ہیں۔",
      rating: 4,
    },
  ] : [
    {
      name: "Mahmood Nawaz Shah",
      role: "GDelight Farm, Sindh",
      text: "We have utilized the services of AgriCheck for more than a year now. We are very excited to receive real-time reliable information from the field. In Pakistan it is a challenge developing this technology and making it workable on the field. We are hoping to continue our work and expand beyond mangoes and banana.",
      rating: 5,
    },
    {
      name: "Ahmed Khan",
      role: "Wheat Farmer, Punjab",
      text: "AgriCheck transformed how I manage my fields. The real-time NPK data alone saved me 20% on fertilizer costs last season. The sensor probes give accurate underground readings that help me make better irrigation decisions.",
      rating: 5,
    },
    {
      name: "Fatima Bibi",
      role: "Vegetable Grower, Sindh",
      text: "The AI advisor speaks Urdu  that was a game changer for me. I get crop recommendations I can actually understand and act on. The weekly reports from agronomists keep me on track throughout the growing season.",
      rating: 5,
    },
    {
      name: "Rashid Ali",
      role: "Rice Farmer, KPK",
      text: "I deployed sensors across my paddies. The satellite imagery combined with soil data helped me identify drainage issues I'd been ignoring for years. My water usage dropped by 35% in one season.",
      rating: 4,
    },
    {
      name: "Tariq Mehmood",
      role: "Sugarcane Farmer, Multan",
      text: "Soil temperature and humidity monitoring helped me optimize my irrigation schedule. The pest prediction feature saved my crop from a major attack. My yield went up 25% in one season.",
      rating: 5,
    },
    {
      name: "Nadia Hussain",
      role: "Organic Farm Owner, Islamabad",
      text: "Finally, a platform that gives me the data I need without the complexity. Setup was simple and support has been excellent. The monthly field visits by their agronomists are incredibly valuable.",
      rating: 4,
    },
  ];

  return (
    <StaticPageLayout>
      <section className="py-20 px-6 bg-gradient-to-br from-primary/10 via-background to-accent/20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
          {isUrdu ? "تجربات" : "Testimonials"}
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-foreground mb-4">
          {isUrdu ? "لوگ ہمارے بارے میں کیا کہتے ہیں" : "What People Say About Us"}
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {isUrdu
            ? "کاشتکاری کی صنعت کے پیشہ ور افراد کے کچھ اقتباسات یہ ہیں۔ ان میں سے 80٪ کاشتکار ہماری خدمات دوسروں کو تجویز کریں گے۔ دیکھیں لوگ ایگری چیک کے بارے میں کیا کہہ رہے ہیں۔"
            : "Here are some quotes from professionals in the farming industry. 80% of these farmers would recommend our services to others. Take a look at what people are saying about AgriCheck."}
        </p>
      </section>

      <section className="py-16 px-6 bg-background">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((item) => (
            <div key={item.name} className="rounded-xl border border-border bg-card p-8 space-y-4 hover:shadow-lg hover:border-primary/30 transition-all duration-300 relative">
              <Quote className="w-8 h-8 text-primary/20 absolute top-6 right-6" />
              <div className="flex gap-1">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className={`w-4 h-4 ${i < item.rating ? "text-warning fill-warning" : "text-muted-foreground"}`} />
                ))}
              </div>
              <p className="text-muted-foreground italic leading-relaxed">"{item.text}"</p>
              <div className="pt-2 border-t border-border">
                <div className="font-semibold text-card-foreground">{item.name}</div>
                <div className="text-sm text-muted-foreground">{item.role}</div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </StaticPageLayout>
  );
}
