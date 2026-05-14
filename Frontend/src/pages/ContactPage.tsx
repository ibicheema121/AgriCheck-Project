import { StaticPageLayout } from "@/components/StaticPageLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Mail, Phone, MapPin, Facebook, Instagram, Linkedin, Youtube } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { useLanguage } from "@/contexts/LanguageContext";

export default function ContactPage() {
  const { toast } = useToast();
  const { language } = useLanguage();
  const isUrdu = language === "ur";
  const [sending, setSending] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSending(true);
    setTimeout(() => {
      setSending(false);
      toast({
        title: isUrdu ? "پیغام بھیج دیا گیا" : "Message Sent",
        description: isUrdu ? "ہم 24 گھنٹوں کے اندر آپ سے رابطہ کریں گے۔" : "We'll get back to you within 24 hours.",
      });
      (e.target as HTMLFormElement).reset();
    }, 1000);
  };

  const contactItems = isUrdu ? [
    { icon: Mail, label: "ای میل", value: "support@agricheck.io" },
    { icon: Phone, label: "فون", value: "+92 300 1234567" },
    { icon: MapPin, label: "پتہ", value: "لاہور، پنجاب، پاکستان" },
  ] : [
    { icon: Mail, label: "Email", value: "support@agricheck.io" },
    { icon: Phone, label: "Phone", value: "+92 300 1234567" },
    { icon: MapPin, label: "Address", value: "Lahore, Punjab, Pakistan" },
  ];

  return (
    <StaticPageLayout>
      <section className="py-20 px-6 bg-gradient-to-br from-primary/10 via-background to-accent/20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-4">
          {isUrdu ? "ہم سے رابطہ کریں" : "Get In Touch"}
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-foreground mb-4">
          {isUrdu ? "ہم سے رابطہ کریں" : "Contact Us"}
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {isUrdu
            ? "ہم آپ کی رائے اور تجاویز کی قدر کرتے ہیں۔ سوالات ہیں؟ رابطہ کریں اور ہماری ٹیم 24 گھنٹوں کے اندر جواب دے گی۔"
            : "We appreciate your feedback and recommendations. Have questions? Reach out and our team will respond within 24 hours."}
        </p>
      </section>

      <section className="py-16 px-6 bg-background">
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-12">
          {/* Contact Info */}
          <div className="space-y-8">
            <h2 className="text-2xl font-bold text-foreground">
              {isUrdu ? "ہم سے رابطہ کریں" : "Get in Touch"}
            </h2>
            {contactItems.map((item) => (
              <div key={item.label} className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <item.icon className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <div className="font-medium text-foreground">{item.label}</div>
                  <div className="text-muted-foreground">{item.value}</div>
                </div>
              </div>
            ))}

            {/* Social Links */}
            <div className="pt-4">
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">
                {isUrdu ? "ہمیں فالو کریں" : "Follow Us"}
              </h3>
              <div className="flex gap-3">
                {[
                  { icon: Facebook, href: "#" },
                  { icon: Instagram, href: "#" },
                  { icon: Linkedin, href: "#" },
                  { icon: Youtube, href: "#" },
                ].map((social, i) => (
                  <a key={i} href={social.href} className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors">
                    <social.icon className="w-5 h-5" />
                  </a>
                ))}
              </div>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="rounded-xl border border-border bg-card p-8 space-y-5">
            <div className="space-y-2">
              <Label htmlFor="name">{isUrdu ? "نام" : "Name"}</Label>
              <Input id="name" placeholder={isUrdu ? "آپ کا نام" : "Your name"} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">{isUrdu ? "ای میل" : "Email"}</Label>
              <Input id="email" type="email" placeholder={isUrdu ? "آپ کی ای میل" : "you@example.com"} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="subject">{isUrdu ? "موضوع" : "Subject"}</Label>
              <Input id="subject" placeholder={isUrdu ? "ہم کیسے مدد کر سکتے ہیں؟" : "How can we help?"} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="message">{isUrdu ? "پیغام" : "Message"}</Label>
              <Textarea id="message" placeholder={isUrdu ? "اپنی ضروریات کے بارے میں مزید بتائیں..." : "Tell us more about your needs..."} rows={5} required />
            </div>
            <Button type="submit" className="w-full" disabled={sending}>
              {sending
                ? (isUrdu ? "بھیجا جا رہا ہے..." : "Sending...")
                : (isUrdu ? "پیغام بھیجیں" : "Send Message")}
            </Button>
          </form>
        </div>
      </section>
    </StaticPageLayout>
  );
}
