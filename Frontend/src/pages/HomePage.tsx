import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Leaf, BarChart3, Bot, Droplets, ArrowRight, Shield, Sprout,
  Globe, Briefcase, MapPin, Waves, Trophy, Users, Cpu, CloudSun,
  TrendingUp, Award, ChevronLeft, ChevronRight, ShoppingCart
} from "lucide-react";
import { StaticPageLayout } from "@/components/StaticPageLayout";
import { useState, useEffect, useCallback } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import { motion } from "framer-motion";

/* ───────────── HERO SLIDESHOW ───────────── */

const heroSlidesData = {
  en: [
    {
      image: "/images/hero1.png",
      badge: "Smart Agriculture Platform",
      title: "Precision Farming for Modern Agriculture",
      subtitle: "The future of farming  drive crop and business growth with data-driven decisions. Automate your farm using IoT and AI-based tools.",
      cta: "Get Started",
      ctaLink: "/login",
    },
    {
      image: "/images/hero2.png",
      badge: "Data Driven Crop Monitoring",
      title: "Monitor Your Crops with Real-Time Intelligence",
      subtitle: "AgriCheck combines AI and field sensors to give farmers real-time insights on soil, land, and weather  from ploughing to harvesting.",
      cta: "Our Services",
      ctaLink: "/services",
    },
    {
      image: "/images/hero3.png",
      badge: "Satellite & IoT Solutions",
      title: "All-In-One Digital Farming Solution",
      subtitle: "Satellite imagery, soil sensor probes, weather forecasts, pest prediction, and agronomist advisory  all in one platform.",
      cta: "Contact Us",
      ctaLink: "/contact",
    },
  ],
  ur: [
    {
      image: "/images/hero1.png",
      badge: "سمارٹ زراعت پلیٹ فارم",
      title: "جدید زراعت کے لیے درست کاشتکاری",
      subtitle: "کاشتکاری کا مستقبل  ڈیٹا پر مبنی فیصلوں سے فصل اور کاروبار کی ترقی کریں۔ IoT اور AI ٹولز کا استعمال کرتے ہوئے اپنے فارم کو خودکار بنائیں۔",
      cta: "شروع کریں",
      ctaLink: "/login",
    },
    {
      image: "/images/hero2.png",
      badge: "ڈیٹا پر مبنی فصل نگرانی",
      title: "ریئل ٹائم انٹیلیجنس سے اپنی فصلوں کی نگرانی کریں",
      subtitle: "ایگری چیک AI اور فیلڈ سینسرز کو یکجا کرتا ہے تاکہ کاشتکاروں کو مٹی، زمین اور موسم کے بارے میں جوتنے سے کٹائی تک ریئل ٹائم سمجھ مل سکے۔",
      cta: "ہماری خدمات",
      ctaLink: "/services",
    },
    {
      image: "/images/hero3.png",
      badge: "سیٹلائٹ اور IoT حل",
      title: "ڈیجیٹل کاشتکاری کا آل-ان-ون حل",
      subtitle: "سیٹلائٹ امیجری، مٹی کے سینسر پروبز، موسمی پیشگوئیاں، کیڑوں کی پیش گوئی اور ماہر زراعت کا مشورہ  سب ایک پلیٹ فارم میں۔",
      cta: "ہم سے رابطہ کریں",
      ctaLink: "/contact",
    },
  ],
};

function HeroSlideshow() {
  const { language } = useLanguage();
  const heroSlides = heroSlidesData[language];
  const [current, setCurrent] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const goTo = useCallback((idx: number) => {
    if (isAnimating) return;
    setIsAnimating(true);
    setCurrent(idx);
    setTimeout(() => setIsAnimating(false), 500);
  }, [isAnimating]);

  const next = useCallback(() => goTo((current + 1) % heroSlides.length), [current, goTo, heroSlides.length]);
  const prev = useCallback(() => goTo((current - 1 + heroSlides.length) % heroSlides.length), [current, goTo, heroSlides.length]);

  useEffect(() => {
    const t = setInterval(next, 5500);
    return () => clearInterval(t);
  }, [next]);

  const slide = heroSlides[current];

  return (
    <section className="relative h-[90vh] min-h-[560px] max-h-[800px] overflow-hidden">
      {heroSlides.map((s, i) => (
        <div key={i} className={`absolute inset-0 transition-opacity duration-700 ${i === current ? "opacity-100" : "opacity-0"}`}>
          <img src={s.image} alt={s.title} className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/40 to-transparent" />
        </div>
      ))}

      <div className="relative z-10 h-full flex items-center px-8 md:px-16 lg:px-24">
        <div key={current} className="max-w-2xl space-y-6 animate-in fade-in slide-in-from-left-8 duration-500">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm text-white text-sm font-medium border border-white/30">
            <Leaf className="w-4 h-4" />
            {slide.badge}
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-tight drop-shadow-lg">
            {slide.title}
          </h1>
          <p className="text-lg text-white/85 max-w-xl leading-relaxed drop-shadow">{slide.subtitle}</p>
          <div className="flex flex-wrap gap-4 pt-2">
            <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg" asChild>
              <Link to={slide.ctaLink}>{slide.cta} <ArrowRight className="w-4 h-4 ml-1" /></Link>
            </Button>
            <Button size="lg" variant="outline" className="border-white/50" asChild>
              <Link to="/about">{language === "ur" ? "مزید جانیں" : "Learn More"}</Link>
            </Button>
          </div>
        </div>
      </div>

      <button onClick={prev} className="absolute left-4 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-white/20 hover:bg-white/40 backdrop-blur-sm flex items-center justify-center text-white border border-white/30 transition-all">
        <ChevronLeft className="w-5 h-5" />
      </button>
      <button onClick={next} className="absolute right-4 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-white/20 hover:bg-white/40 backdrop-blur-sm flex items-center justify-center text-white border border-white/30 transition-all">
        <ChevronRight className="w-5 h-5" />
      </button>

      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex gap-2">
        {heroSlides.map((_, i) => (
          <button key={i} onClick={() => goTo(i)} className={`rounded-full transition-all duration-300 ${i === current ? "w-8 h-2.5 bg-primary" : "w-2.5 h-2.5 bg-white/50 hover:bg-white/80"}`} />
        ))}
      </div>
    </section>
  );
}

/* ───────────── MAIN PAGE ───────────── */

export default function HomePage() {
  const { language } = useLanguage();

  const missionItems = language === "ur" ? [
    { icon: Shield, title: "غذائی تحفظ", desc: "ڈیٹا پر مبنی فیصلوں کے ذریعے خوراک کی مناسب فراہمی اور غذائی تحفظ کو یقینی بنانا۔" },
    { icon: Sprout, title: "نامیاتی خوراک", desc: "صحت مند، اعلیٰ معیار، غذائیت سے بھرپور اور نامیاتی خوراک کی پیداوار کو فروغ دینا۔" },
    { icon: Globe, title: "زمین کی بحالی", desc: "درست نگرانی کے ذریعے اعلیٰ معیار کی زمینی بحالی فراہم کرکے زمین کا تحفظ کرنا۔" },
    { icon: TrendingUp, title: "سستی", desc: "سمارٹ تجزیات کے ساتھ فصلی آدانوں کو بہتر بنا کر کاشتکاروں کی سستی میں اضافہ کرنا۔" },
    { icon: Briefcase, title: "روزگار کی تخلیق", desc: "زراعت ٹیکنالوجی میں لوگوں کو زندگی بدلنے والے کیریئر میں ترقی دینا، رکھنا اور سہارا دینا۔" },
    { icon: MapPin, title: "ٹریکنگ اور ٹریس ایبلٹی", desc: "ڈیٹا پر مبنی فیصلے کرنے کے لیے فارموں اور کھیتوں کی ٹریکنگ اور ٹریس ایبلٹی فراہم کرنا۔" },
    { icon: Waves, title: "پانی بچائیں", desc: "ریئل ٹائم مٹی کی نمی کی نگرانی کے ذریعے آبپاشی کو بہتر بنا کر پانی کے وسائل کا تحفظ۔" },
  ] : [
    { icon: Shield, title: "Food Security", desc: "Ensuring production of adequate food supplies and achieving food security through data-driven decisions." },
    { icon: Sprout, title: "Organic Food", desc: "Promoting production of the healthiest, highest quality, nutritious and organic food." },
    { icon: Globe, title: "Land Reclamation", desc: "Preserving the earth by providing highest quality land reclamation through precision monitoring." },
    { icon: TrendingUp, title: "Affordability", desc: "Increasing farmer affordability by optimizing and monitoring crop inputs with smart analytics." },
    { icon: Briefcase, title: "Employment Generation", desc: "Developing, placing and supporting people into life-changing careers in agriculture technology." },
    { icon: MapPin, title: "Tracking & Traceability", desc: "Providing tracking and traceability of farms and fields to make data-driven decisions." },
    { icon: Waves, title: "Save Water", desc: "Optimizing irrigation through real-time soil moisture monitoring to conserve water resources." },
  ];

  const servicePreview = language === "ur" ? [
    { icon: Droplets, title: "آبپاشی نسخہ", desc: "ریئل ٹائم مٹی کی نمی کے ٹریکنگ اور آبپاشی کی پیشگوئیوں کے ساتھ صحیح وقت پر پانی کی صحیح مقدار۔" },
    { icon: Bot, title: "AI مشاورت", desc: "آبپاشی، فصل کی صحت، پانی جمع ہونے اور کھاد کی ضروریات کے لیے بروقت سفارشات۔" },
    { icon: CloudSun, title: "موسمی اپ ڈیٹس", desc: "انتہائی موسمی حالات کی پیش گوئی اور فصلوں کے تحفظ کے لیے ریئل ٹائم موسمی اپ ڈیٹس اور پیشگوئیاں۔" },
    { icon: Cpu, title: "سینسر پروبز", desc: "مکمل ریئل ٹائم زیر زمین نگرانی  مٹی کی نمی، درجہ حرارت، EC، نمکیات، TDS، اور NPK۔" },
    { icon: BarChart3, title: "سیٹلائٹ امیجری", desc: "تاریخ کے مطابق سیٹلائٹ تصاویر NDVI، EVI، NDWI، NDRE اور NDMI ویجیٹیشن انڈیسز کے ساتھ۔" },
    { icon: Leaf, title: "مٹی کے غذائی اجزاء کا تجزیہ", desc: "غذائی مواد کی نگرانی، کمیوں کی شناخت، اور کھاد کی سفارشات حاصل کریں۔" },
  ] : [
    { icon: Droplets, title: "Irrigation Prescription", desc: "Right amount of water at the right time, with real-time soil moisture tracking and irrigation forecasts." },
    { icon: Bot, title: "AI Advisory", desc: "On-time recommendations for irrigation, crop health, water-logging and fertilizer requirements." },
    { icon: CloudSun, title: "Weather Updates", desc: "Real-time weather updates and forecasts to predict extreme conditions and protect crops." },
    { icon: Cpu, title: "Sensor Probes", desc: "Complete real-time underground monitoring  soil moisture, temperature, EC, salinity, TDS, and NPK." },
    { icon: BarChart3, title: "Satellite Imagery", desc: "Date-wise satellite images with NDVI, EVI, NDWI, NDRE & NDMI vegetation indices." },
    { icon: Leaf, title: "Soil Nutrient Analysis", desc: "Monitor nutrient content, identify deficiencies, and get fertilizer recommendations." },
  ];

  const products = language === "ur" ? [
    { image: "/images/product1.png", title: "سیٹلائٹ اور IoT فصل نگرانی پلان", desc: "مکمل سیٹلائٹ امیجری + IoT سینسر انٹیگریشن جامع فارم نگرانی کے لیے۔", badge: "سب سے مقبول" },
    { image: "/images/product3.png", title: "ہفتہ وار تجزیاتی رپورٹس", desc: "فضائی امیجری اور سفارشات کے ساتھ پیشہ ور ہفتہ وار اور ماہانہ ماہر زراعت رپورٹس۔", badge: "نیا" },
    { image: "/images/product2.png", title: "سینسر پروبز کٹ", desc: "فیلڈ گریڈ NPK، pH، EC، درجہ حرارت اور نمی سینسر پروبز  پلگ اینڈ پلے تعیناتی۔", badge: "ہارڈ ویئر" },
    { image: "/images/product4.png", title: "موسمی ٹریکر اسٹیشن", desc: "دور دراز فارموں کے لیے سولر پاورڈ GSM موسمی اسٹیشن  بارش، درجہ حرارت، ہوا اور نمی۔", badge: "ہارڈ ویئر" },
  ] : [
    { image: "/images/product1.png", title: "Satellite & IoT Crop Monitoring Plan", desc: "Complete satellite imagery + IoT sensor integration for comprehensive farm monitoring.", badge: "Most Popular" },
    { image: "/images/product3.png", title: "Weekly Analytics Reports", desc: "Professional weekly and monthly agronomist reports with aerial imagery and recommendations.", badge: "New" },
    { image: "/images/product2.png", title: "Sensor Probes Kit", desc: "Field-grade NPK, pH, EC, temperature and moisture sensor probes  plug-and-play deployment.", badge: "Hardware" },
    { image: "/images/product4.png", title: "Weather Tracker Station", desc: "Solar-powered GSM weather station for remote farms  rainfall, temperature, wind, and humidity.", badge: "Hardware" },
  ];

  const achievements = language === "ur" ? [
    { icon: Users, value: "500+", label: "نگرانی شدہ فارم" },
    { icon: Cpu, value: "10,000+", label: "تعینات سینسرز" },
    { icon: TrendingUp, value: "30%", label: "اوسط پیداوار میں اضافہ" },
    { icon: Waves, value: "40%", label: "پانی کی بچت" },
    { icon: Trophy, value: "15+", label: "جیتے گئے ایوارڈز" },
    { icon: Award, value: "98%", label: "کلائنٹ کی اطمینان" },
  ] : [
    { icon: Users, value: "500+", label: "Farms Monitored" },
    { icon: Cpu, value: "10,000+", label: "Sensors Deployed" },
    { icon: TrendingUp, value: "30%", label: "Avg. Yield Increase" },
    { icon: Waves, value: "40%", label: "Water Saved" },
    { icon: Trophy, value: "15+", label: "Awards Won" },
    { icon: Award, value: "98%", label: "Client Satisfaction" },
  ];

  const isUrdu = language === "ur";

  return (
    <StaticPageLayout>
      {/* Hero Slideshow */}
      <HeroSlideshow />

      {/* Welcome */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider">
              {isUrdu ? "ایگری چیک میں خوش آمدید" : "Welcome To AgriCheck"}
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground leading-tight">
              {isUrdu
                ? "اپنی فصلوں کو بالکل وہ دیں جو انہیں چاہیے، جب انہیں چاہیے"
                : "Giving Your Crops Exactly What They Need, When They Need"}
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              {isUrdu
                ? "ایگری چیک کنٹرولڈ اور بڑے پیمانے پر کاشتکاری کی سہولیات تیار کرکے زراعت کو نئی شکل دے رہا ہے۔ ہمارے ڈیٹا سائنسدانوں، سافٹ ویئر ڈویلپرز، ہارڈ ویئر انجینئرز اور ماہرین زراعت کی ٹیم کا مقصد کاشتکاری کو سمارٹ اور زیادہ درست بنانا ہے۔"
                : "AgriCheck is redefining agriculture by developing controlled and large-scale farming facilities. Our team of data scientists, software developers, hardware engineers and agronomists aim to make farming smart and more precise."}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              {isUrdu
                ? "ہم مصنوعی ذہانت اور زراعت کے مخصوص ٹولز کو یکجا کرتے ہیں تاکہ مٹی، زمین اور موسمی حالات پر ڈیٹا پر مبنی سمجھ فراہم کی جا سکے جس سے پیداوار میں اضافہ اور آپریشنل اخراجات میں کمی ہو۔"
                : "We combine Artificial Intelligence and Ag-specific tools to provide data-driven insights on soil, land and weather conditions to increase yields and reduce operational costs."}
            </p>
            <div className="flex gap-4 pt-2">
              <Button asChild>
                <Link to="/about">{isUrdu ? "ہمارے بارے میں" : "About Us"} <ArrowRight className="w-4 h-4 ml-1" /></Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/services">{isUrdu ? "ہماری خدمات" : "Our Services"}</Link>
              </Button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-4 bg-primary/5 rounded-3xl" />
            <img src="/images/welcome.png" alt="AgriCheck sensor in field" className="relative w-full h-80 md:h-96 object-cover rounded-2xl shadow-2xl border border-border" />
            <div className="absolute -bottom-4 -left-4 bg-card rounded-xl p-4 shadow-lg border border-border flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-primary" />
              </div>
              <div>
                <div className="text-xl font-bold text-foreground">30%</div>
                <div className="text-xs text-muted-foreground">{isUrdu ? "اوسط پیداوار میں اضافہ" : "Avg. Yield Increase"}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Mission */}
      <section className="py-20 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
              {isUrdu ? "ہمارا مشن" : "Our Mission"}
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              {isUrdu ? "ہمیں آگے کیا بڑھاتا ہے" : "What Drives Us Forward"}
            </h2>
          </div>
          <div className="flex flex-wrap justify-center gap-6 max-w-6xl mx-auto">
            {missionItems.map((item) => (
              <div
                key={item.title}
                className="w-full sm:w-[48%] lg:w-[30%] xl:w-[22%] rounded-xl border border-border bg-card p-6 space-y-3 hover:shadow-lg hover:border-primary/30 transition-all duration-300 group"
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <item.icon className="w-6 h-6 text-primary" />
                </div>

                <h3 className="text-lg font-semibold text-card-foreground">
                  {item.title}
                </h3>

                <p className="text-sm text-muted-foreground leading-relaxed">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>


        </div>
      </section>

      {/* What We Do */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
              {isUrdu ? "ہم کیا کرتے ہیں" : "What We Do"}
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              {isUrdu ? "ڈیجیٹل کاشتکاری کا آل-ان-ون حل" : "All-In-One Digital Farming Solution"}
            </h2>
            <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
              {isUrdu ? "آپ کی ہر ضرورت کے لیے مکمل فصل نگرانی حل فراہم کرنا۔" : "Providing a complete crop monitoring solution for your every need."}
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center mb-12">
            <div className="relative order-2 md:order-1">
              <img src="/images/hero2.png" alt="Farmer with data tablet" className="w-full h-72 object-cover rounded-2xl shadow-xl border border-border" />
              <div className="absolute -top-4 -right-4 bg-primary rounded-xl p-3 shadow-lg">
                <Cpu className="w-6 h-6 text-primary-foreground" />
              </div>
            </div>
            <div className="order-1 md:order-2 space-y-4">
              {servicePreview.slice(0, 3).map((s) => (
                <div key={s.title} className="flex items-start gap-4 p-4 rounded-xl border border-border bg-card hover:border-primary/30 hover:shadow-md transition-all duration-300 group">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 group-hover:bg-primary/20 transition-colors">
                    <s.icon className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-card-foreground">{s.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center mb-12">
            <div className="space-y-4">
              {servicePreview.slice(3).map((s) => (
                <div key={s.title} className="flex items-start gap-4 p-4 rounded-xl border border-border bg-card hover:border-primary/30 hover:shadow-md transition-all duration-300 group">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 group-hover:bg-primary/20 transition-colors">
                    <s.icon className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-card-foreground">{s.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="relative">
              <img src="/images/hero3.png" alt="Satellite farm monitoring" className="w-full h-72 object-cover rounded-2xl shadow-xl border border-border" />
              <div className="absolute -top-4 -left-4 bg-primary rounded-xl p-3 shadow-lg">
                <BarChart3 className="w-6 h-6 text-primary-foreground" />
              </div>
            </div>
          </div>

          <div className="text-center">
            <Button variant="outline" size="lg" asChild>
              <Link to="/services">{isUrdu ? "تمام خدمات دیکھیں" : "View All Services"} <ArrowRight className="w-4 h-4 ml-1" /></Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Our Products */}
      <section className="py-20 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
              <ShoppingCart className="w-3.5 h-3.5" />
              {isUrdu ? "ہماری مصنوعات" : "Our Products"}
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              {isUrdu ? "ایگری چیک پروڈکٹ سوٹ" : "AgriCheck Product Suite"}
            </h2>
            <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
              {isUrdu
                ? "آپ کے کاشتکاری سفر کے ہر مرحلے کے لیے ہارڈ ویئر اور سافٹ ویئر حل۔"
                : "Hardware and software solutions designed for every stage of your farming journey."}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((p) => (
              <div key={p.title} className="rounded-xl border border-border bg-card overflow-hidden hover:shadow-xl hover:border-primary/30 transition-all duration-300 group">
                <div className="relative overflow-hidden h-44">
                  <img src={p.image} alt={p.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  <div className="absolute top-3 left-3">
                    <span className="px-2 py-1 rounded-full bg-primary text-primary-foreground text-xs font-semibold">{p.badge}</span>
                  </div>
                </div>
                <div className="p-5 space-y-3">
                  <h3 className="font-semibold text-card-foreground leading-snug">{p.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{p.desc}</p>
                  <Button size="sm" variant="outline" className="w-full group-hover:border-primary group-hover:text-primary transition-colors" asChild>
                    <Link to="/contact">{isUrdu ? "قیمت معلوم کریں" : "Get a Quote"}</Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Our Achievements */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
              <Trophy className="w-3.5 h-3.5" />
              {isUrdu ? "ہماری کامیابیاں" : "Our Achievements"}
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              {isUrdu ? "بولنے والے اعداد و شمار" : "Numbers That Speak"}
            </h2>
            <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
              {isUrdu
                ? "ٹیکنالوجی اور جدت کے ذریعے زراعت کو تبدیل کرنے میں ہمارا اثر۔"
                : "Our impact in transforming agriculture through technology and innovation."}
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {achievements.map((a, index) => (
              <motion.div
                key={a.label}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05 }}
                className="rounded-xl border border-border bg-card p-6 text-center space-y-3 hover:shadow-lg hover:border-primary/30 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                  <a.icon className="w-6 h-6 text-primary" />
                </div>

                <div className="text-3xl font-extrabold text-primary">{a.value}</div>

                <div className="text-sm text-muted-foreground font-medium">
                  {a.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-primary text-primary-foreground text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold">
            {isUrdu ? "اپنے فارم کو تبدیل کرنے کے لیے تیار ہیں؟" : "Ready to Transform Your Farm?"}
          </h2>
          <p className="text-primary-foreground/80 text-lg">
            {isUrdu
              ? "ایگری چیک استعمال کرنے والے سینکڑوں کاشتکاروں کے ساتھ شامل ہوں جو ڈیٹا پر مبنی درست زراعت کے ذریعے فصلوں کی پیداوار کو بہتر، پانی کی بچت، اور مٹی کی صحت کو بہتر بناتے ہیں۔"
              : "Join hundreds of farmers using AgriCheck to optimize crop yields, save water, and improve soil health with data-driven precision agriculture."}
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button size="lg" variant="secondary" asChild>
              <Link to="/login">{isUrdu ? "شروع کریں" : "Get Started"}</Link>
            </Button>
            <Button size="lg" variant="outline" className="border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10 text-black" asChild>
              <Link to="/contact">{isUrdu ? "ہم سے رابطہ کریں" : "Contact Us"}</Link>
            </Button>
          </div>
        </div>
      </section>
    </StaticPageLayout>
  );
}
