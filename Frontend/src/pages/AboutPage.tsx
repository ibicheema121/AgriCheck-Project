import { StaticPageLayout } from "@/components/StaticPageLayout";
import { Leaf, Target, Eye, Users, Linkedin } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function AboutPage() {
  const { language } = useLanguage();
  const isUrdu = language === "ur";

  const teamMembers = isUrdu ? [
    { name: "سربراہ ماہر زراعت", role: "زرعی تحقیق کے سربراہ", desc: "مٹی سائنس اور فصل انتظام میں ماہر، متعدد فصلوں میں 10 سال سے زیادہ فیلڈ تجربہ۔" },
    { name: "چیف ٹیکنالوجی آفیسر", role: "ٹیکنالوجی اور اختراع سربراہ", desc: "IoT سسٹمز، AI/ML ماڈلز، اور قابل توسیع زرعی ڈیٹا پلیٹ فارمز میں مہارت رکھنے والے سافٹ ویئر آرکیٹیکٹ۔" },
    { name: "ڈیٹا سائنس سربراہ", role: "AI اور تجزیات", desc: "کیڑوں کی پیش گوئی، پیداوار کا تخمینہ، اور مٹی کے غذائی اجزاء کی بہتری کے لیے پیشین گو ماڈل تیار کرتے ہیں۔" },
    { name: "ہارڈویئر انجینئر", role: "IoT اور سینسر سسٹمز", desc: "ریئل ٹائم مٹی اور موسمی ڈیٹا جمع کرنے کے لیے فیلڈ گریڈ سینسر پروبز ڈیزائن اور تعینات کرتے ہیں۔" },
  ] : [
    { name: "Lead Agronomist", role: "Head of Agricultural Research", desc: "Expert in soil science and crop management with 10+ years of field experience across multiple crop varieties." },
    { name: "CTO", role: "Technology & Innovation Lead", desc: "Software architect specializing in IoT systems, AI/ML models, and scalable agricultural data platforms." },
    { name: "Data Science Lead", role: "AI & Analytics", desc: "Develops predictive models for pest prediction, yield estimation, and soil nutrient optimization." },
    { name: "Hardware Engineer", role: "IoT & Sensor Systems", desc: "Designs and deploys field-grade sensor probes for real-time soil and weather data collection." },
  ];

  const missionVision = isUrdu ? [
    {
      icon: Target,
      title: "ہمارا مشن",
      text: "درست زراعت کو جمہوری بنانا تاکہ ریئل ٹائم مٹی کی نگرانی چھوٹے کاشتکاروں سے لے کر بڑے پیمانے تک ہر کاشتکار کے لیے قابل رسائی اور سستی ہو  ڈیٹا پر مبنی فیصلوں کو ممکن بنانا جو وسائل کے ضیاع کو کم کرتے ہوئے پیداوار کو بہتر بناتے ہیں۔",
    },
    {
      icon: Eye,
      title: "ہمارا وژن",
      text: "ٹیکنالوجی اور اختراع کے ذریعے زرعی منظرنامے میں انقلاب۔ ایک ایسی دنیا جہاں ہر زرعی فیصلہ درست مٹی کے ڈیٹا اور ذہین AI سفارشات پر مبنی ہو، جس سے پائیدار، اعلیٰ پیداواری زراعت کا سلسلہ جاری رہے۔",
    },
  ] : [
    {
      icon: Target,
      title: "Our Mission",
      text: "To democratize precision agriculture by making real-time soil monitoring accessible and affordable for every farmer  from smallholders to large-scale operations  enabling data-driven decisions that improve yields while reducing resource waste.",
    },
    {
      icon: Eye,
      title: "Our Vision",
      text: "Revolutionizing the agricultural landscape through technology and innovation. A world where every farming decision is backed by accurate soil data and intelligent AI recommendations, leading to sustainable, high-yield agriculture.",
    },
  ];

  const stats = isUrdu ? [
    { value: "500+", label: "فعال فارم" },
    { value: "10K+", label: "تعینات سینسرز" },
    { value: "98%", label: "اپ ٹائم" },
    { value: "30%", label: "اوسط پیداوار میں اضافہ" },
  ] : [
    { value: "500+", label: "Active Farms" },
    { value: "10K+", label: "Sensors Deployed" },
    { value: "98%", label: "Uptime" },
    { value: "30%", label: "Avg. Yield Increase" },
  ];

  return (
    <StaticPageLayout>
      {/* Hero */}
      <section className="py-20 px-6 bg-gradient-to-br from-primary/10 via-background to-accent/20 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-foreground mb-4">
          {isUrdu ? "ایگری چیک کے بارے میں" : "About AgriCheck"}
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {isUrdu
            ? "جدید AI پر مبنی ٹیکنالوجی کے ساتھ اپنی فصلوں کی پیداوار دوگنی کریں اور اپنے فارموں کو ورچوئلی منظم کریں۔"
            : "Double the production of your crops and manage your farms virtually with innovative AI-based technology."}
        </p>
      </section>

      {/* About Content */}
      <section className="py-16 px-6 bg-background">
        <div className="max-w-4xl mx-auto space-y-10">
          <div className="text-center space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider">
              {isUrdu ? "ہمارا ایک ہی ہدف ہے" : "We Have One Goal"}
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              {isUrdu
                ? "پیداوار کو زیادہ سے زیادہ کرنا، منافع اور سستی میں اضافہ کرنا"
                : "To Maximize Production Yield, Increase Profitability & Affordability"}
            </h2>
          </div>
          <p className="text-muted-foreground leading-relaxed text-center max-w-3xl mx-auto">
            {isUrdu
              ? "ایگری چیک ڈیٹا سائنسدانوں، ہارڈویئر انجینئرز، سافٹ ویئر ڈویلپرز اور ماہرین زراعت کی ایک ورسٹائل ٹیم ہے جو مصنوعی ذہانت اور زراعت کے مخصوص ٹولز کو یکجا کرتے ہیں تاکہ زمین، مٹی اور موسمی حالات کی بنیاد پر ڈیٹا سے چلنے والی سمجھ تیار کر کے اعلیٰ پیداواری فارم بنائے جا سکیں۔"
              : "AgriCheck is a versatile team of data scientists, hardware engineers, software developers and agronomy experts who combine artificial intelligence and ag-specific tools and trends to develop data-driven insights based on land, soil and weather conditions to create high-yield farms."}
          </p>
          <p className="text-muted-foreground leading-relaxed text-center max-w-3xl mx-auto">
            {isUrdu
              ? "ہمارا پلیٹ فارم جوتنے سے کٹائی تک روزانہ کے فارم آپریشنز کا تجزیہ اور بہتری کے لیے تفصیلی معلومات فراہم کرتا ہے۔ کھادوں کی بہترین مقدار کا استعمال، بے ضابطگیوں کا جلد پتہ لگانا، کیڑوں کی پیش گوئی، اور ریئل ٹائم زرعی مشاورت پودوں کو مشکل حالات سے بچا سکتی ہے اور وسائل کے استعمال کو بہتر بنا سکتی ہے۔"
              : "Our platform provides detailed information to analyze and optimize day-to-day farm operations from ploughing to harvesting. Use of optimum quantity of fertilizers, early detection of anomalies, pest prediction, and real-time agronomic advisory can shield plants from tough conditions and enhance their use of resources."}
          </p>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-16 px-6 bg-muted/30">
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-12">
          {missionVision.map((item) => (
            <div key={item.title} className="rounded-xl border border-border bg-card p-8 space-y-4 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <item.icon className="w-6 h-6 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-card-foreground">{item.title}</h2>
              <p className="text-muted-foreground leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Story */}
      <section className="py-16 px-6 bg-background">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <Leaf className="w-10 h-10 text-primary mx-auto" />
          <h2 className="text-3xl font-bold text-foreground">
            {isUrdu ? "ہماری کہانی" : "Our Story"}
          </h2>
          <p className="text-muted-foreground leading-relaxed">
            {isUrdu
              ? "ایگری چیک اس سادہ مشاہدے سے پیدا ہوا کہ زیادہ تر کاشتکاروں کو مٹی کے ڈیٹا تک رسائی نہیں ہے جو باخبر فیصلے کرنے کے لیے ضروری ہے۔ زرعی انجینئرز اور IoT ماہرین کی ایک ٹیم نے اس خلا کو پر کرنے کے لیے AI سے چلنے والے ڈیش بورڈ کے ساتھ ایک کم قیمت سینسر نیٹ ورک بنایا۔ آج، ہمارا پلیٹ فارم متعدد خطوں میں کاشتکاری برادریوں کی خدمت کرتا ہے، کھاد کے ضیاع کو کم کرتے ہوئے پیداوار کو بہتر بنانے اور پانی کے وسائل کو بچانے میں مدد کرتا ہے۔"
              : "AgriCheck was born from the simple observation that most farmers lack access to the soil data needed to make informed decisions. Founded by a team of agricultural engineers and IoT specialists, we built a low-cost sensor network paired with an AI-powered dashboard to bridge that gap. Today, our platform serves farming communities across multiple regions, helping improve yields while reducing fertilizer waste and conserving water resources."}
          </p>
        </div>
      </section>

      {/* Team */}
      <section className="py-16 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
              <Users className="w-3.5 h-3.5" />
              {isUrdu ? "ہماری ٹیم" : "Our Team"}
            </div>
            <h2 className="text-3xl font-bold text-foreground">
              {isUrdu ? "ماہرین سے ملیں" : "Meet the Experts"}
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {teamMembers.map((member) => (
              <div key={member.name} className="rounded-xl border border-border bg-card p-6 text-center space-y-3 hover:shadow-lg hover:border-primary/30 transition-all duration-300">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                  <Users className="w-7 h-7 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-card-foreground">{member.name}</h3>
                <p className="text-sm text-primary font-medium">{member.role}</p>
                <p className="text-sm text-muted-foreground leading-relaxed">{member.desc}</p>
                <div className="flex justify-center gap-2 pt-1">
                  <a href="#" className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors">
                    <Linkedin className="w-4 h-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-6 bg-background">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((stat) => (
            <div key={stat.label}>
              <div className="text-3xl font-extrabold text-primary">{stat.value}</div>
              <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>
    </StaticPageLayout>
  );
}
