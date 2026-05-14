import { StaticPageLayout } from "@/components/StaticPageLayout";
import {
  Droplets, Users, CloudSun, Cpu, FlaskConical, FileText,
  MapPin, Satellite, Bug, Leaf
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function ServicesPage() {
  const { language } = useLanguage();
  const isUrdu = language === "ur";

  const services = isUrdu ? [
    { icon: Droplets, title: "آبپاشی نسخہ", desc: "فصل کی پیداوار بڑھانے کے لیے صحیح وقت پر پانی کی صحیح مقدار ضروری ہے۔ ایگری چیک سینسرز کا استعمال کرتے ہوئے، کاشتکاروں کو فصل کے مرحلے، فصل میں موجودہ پانی کی سطح کے بارے میں آگاہ کیا جاتا ہے، اور آبپاشی کی پیشگوئیاں بھی فراہم کی جاتی ہیں۔" },
    { icon: Users, title: "ماہر زراعت کی مشاورت", desc: "ہمارے ماہرین زراعت کاشتکاروں کے ساتھ مل کر آبپاشی، فصل کی صحت، پانی جمع ہونے اور کھاد کی ضروریات کے بارے میں بروقت سفارشات فراہم کرکے فصلوں کی منافع بخشی میں اضافہ یقینی بناتے ہیں۔" },
    { icon: CloudSun, title: "موسمی اپ ڈیٹس اور پیشگوئی", desc: "ریئل ٹائم موسمی اپ ڈیٹس اور پیشگوئیاں آپ کو روزانہ کے فیصلے کرنے میں مدد کرتی ہیں۔ مسلسل موسمی نگرانی انتہائی موسمی حالات کی پیشگوئی کرتی ہے تاکہ فصلوں کو ضرورت سے زیادہ نقصان سے بچایا جا سکے۔" },
    { icon: Cpu, title: "سینسر پروبز", desc: "ایگری چیک سینسر پروبز آپ کو مکمل ریئل ٹائم زیر زمین موسمی نقشہ فراہم کرتے ہیں۔ یہ سب سے تفصیلی اور درست ریئل ٹائم مٹی کے معیار کا ڈیٹا فراہم کرتے ہیں  مٹی کی نمی، درجہ حرارت، EC، نمکیات، TDS، اور مختلف گہرائیوں پر NPK۔" },
    { icon: FlaskConical, title: "مٹی کے نمونے اور ٹیسٹ رپورٹس", desc: "مٹی کے نمونے لینا مٹی کا pH، غذائی سطح اور نامیاتی مادے جیسے اہم پیرامیٹرز کا جائزہ لینے کے لیے ایک لازمی عمل ہے۔ ہمارے ماہرین زراعت فیلڈ سے مٹی کے نمونے لیتے ہیں، لیبارٹری تجزیہ کرتے ہیں اور کاشتکاروں کو ٹیسٹ رپورٹس فراہم کرتے ہیں۔" },
    { icon: FileText, title: "ہفتہ وار / ماہانہ رپورٹس", desc: "ہماری رپورٹس آپ کے فارم اور فصل کی صحت کی پیشرفت کی حقیقی تصویر ہیں جو ہمارے ماہرین زراعت ہفتہ وار اور ماہانہ بنیاد پر فراہم کرتے ہیں۔ ان میں فضائی تصاویر، ویجیٹیٹو گروتھ نقشے، اور تحریری سفارشات شامل ہیں۔" },
    { icon: MapPin, title: "فیلڈ وزٹس", desc: "آپ کے فارموں کو ورچوئلی منظم کرنے کے علاوہ، ہمارے ماہرین زراعت فارم کی ضروریات کا جائزہ لینے، بصری مشاہدات کرنے اور اعلیٰ معیار کی فصلی پیداوار کو یقینی بنانے کے لیے حکمت عملی وضع کرنے کے لیے آپ کے کھیتوں کا ماہانہ دورہ کرتے ہیں۔" },
    { icon: Satellite, title: "سیٹلائٹ امیجری", desc: "ایگری چیک فصل کی صحت کی حالت، پانی جمع ہونے کی موجودگی، اور NDVI، EVI، NDWI، NDRE اور NDMI سمیت ویجیٹیشن انڈیسز تعین کرنے کے لیے آپ کے فیلڈ کی تاریخ کے مطابق سیٹلائٹ تصاویر فراہم کرتا ہے۔" },
    { icon: Bug, title: "کیڑوں کی پیش گوئی اور کنٹرول", desc: "فصلوں کو رکے ہوئے نمو اور پیداواری صلاحیت میں کمی سے بچانے کے لیے، کاشتکاروں کو کیڑوں کے کنٹرول کے لیے مناسب منصوبے کی ضرورت ہے۔ ایگری چیک کیڑوں کے حملوں کی پیشگوئی پہلے سے کرتا ہے اور فصلوں کو صحت مند رکھنے کے لیے کنٹرول سفارشات فراہم کرتا ہے۔" },
    { icon: Leaf, title: "مٹی کے غذائی اجزاء کا تجزیہ", desc: "ہمارے ٹولز اور سافٹ ویئر سسٹم مٹی میں موجود غذائی مواد کی مقدار کی نگرانی کرتے ہیں۔ یہ پیداوار کی قسم کی بنیاد پر غذائی کمیوں کی شناخت کرتا ہے اور کاشتکاروں کو فصل کی ضروری نشوونما کے لیے درکار کھاد کی مقدار کی سفارش کرتا ہے۔" },
  ] : [
    { icon: Droplets, title: "Irrigation Prescription", desc: "Right amount of water, at the right time is essential for increasing your crop production. Using AgriCheck sensors, farmers are updated about the crop stage, current water level present in the crops, and irrigation forecasts are also provided." },
    { icon: Users, title: "Agronomist Advisory", desc: "Our agronomists work together with farmers and growers by providing on-time recommendations concerning irrigation, crop health, water logging and fertilizer requirements to ensure the increase in profitability of crops." },
    { icon: CloudSun, title: "Weather Updates & Forecast", desc: "Real-time weather updates and forecasts help you make day-to-day decisions. Continuous weather monitoring predicts extreme weather conditions beforehand to save crops from excessive damage." },
    { icon: Cpu, title: "Sensor Probes", desc: "AgriCheck sensor probes give you a complete real-time underground weather map. They provide the most detailed and accurate real-time soil quality data  soil moisture, temperature, EC, salinity, TDS, and NPK at different depths." },
    { icon: FlaskConical, title: "Soil Sampling & Test Reports", desc: "Soil sampling is an integral process to evaluate important parameters like soil pH, nutrient levels and organic matter. Our agronomists take soil samples from the field, perform laboratory analysis and provide test reports to growers." },
    { icon: FileText, title: "Weekly / Monthly Reports", desc: "Our reports are a true depiction of your farm and crop health progress provided by our agronomists on a weekly & monthly basis. They include aerial images, vegetative growth maps, and written recommendations." },
    { icon: MapPin, title: "Field Visits", desc: "Apart from virtually managing your farms, our agronomists pay monthly visits to your fields to evaluate farm requirements, perform visual observations and devise strategies to ensure the production of high quality crop yield." },
    { icon: Satellite, title: "Satellite Imagery", desc: "AgriCheck provides date-wise satellite images of your field to determine crop health conditions, presence of water logging, and vegetation indices including NDVI, EVI, NDWI, NDRE & NDMI." },
    { icon: Bug, title: "Pest Prediction & Control", desc: "To save crops from stunted growth & reduction in production capacity, farmers need a proper plan for pest control. AgriCheck predicts pest attacks in advance & provides control recommendations to keep crops healthy." },
    { icon: Leaf, title: "Soil Nutrient Analysis", desc: "Our tools and software system monitor the amount of nutrient content present in the soil. It identifies nutrient deficiencies based on yield type and recommends farmers the amount of fertilizer needed for essential crop growth." },
  ];

  return (
    <StaticPageLayout>
      <section className="py-20 px-6 bg-gradient-to-br from-primary/10 via-background to-accent/20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
          {isUrdu ? "ہم کیا کرتے ہیں" : "What We Do"}
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-foreground mb-4">
          {isUrdu ? "ہماری خدمات" : "Our Services"}
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {isUrdu
            ? "سینسر ہارڈ ویئر سے لے کر AI پر مبنی بصیرت اور ماہر زرعی مشاورت تک  مکمل فصل نگرانی حل۔"
            : "Providing a complete crop monitoring solution  from sensor hardware to AI-powered insights and expert agronomist advisory."}
        </p>
      </section>

      <section className="py-16 px-6 bg-background">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((s) => (
            <div key={s.title} className="rounded-xl border border-border bg-card p-8 space-y-4 hover:shadow-lg hover:border-primary/30 transition-all duration-300 group">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <s.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-card-foreground">{s.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </StaticPageLayout>
  );
}
