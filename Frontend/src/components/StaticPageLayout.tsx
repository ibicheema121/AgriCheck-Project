import { Link, useLocation } from "react-router-dom";
import { Leaf, Facebook, Instagram, Linkedin, Youtube, Mail, Phone, MapPin, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatAssistant } from "@/components/ChatAssistant";
import { useLanguage } from "@/contexts/LanguageContext";

export function StaticPageLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { language, setLanguage, t, dir } = useLanguage();

  const navLinks = [
    { path: "/", label: t("navHome") },
    { path: "/about", label: t("navAbout") },
    { path: "/services", label: t("navServices") },
    { path: "/testimonials", label: t("navTestimonials") },
    { path: "/contact", label: t("navContact") },
  ];

  const toggleLanguage = () => setLanguage(language === "en" ? "ur" : "en");

  return (
    <div className="min-h-screen flex flex-col bg-background" dir={dir}>
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b border-border bg-card/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-primary" />
            </div>
            <span className="text-lg font-bold text-foreground">{t("appName")}</span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${location.pathname === link.path
                    ? "text-primary bg-primary/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            {/* Language Toggle Button */}
            <button
              onClick={toggleLanguage}
              title={language === "en" ? "Switch to Urdu" : "Switch to English"}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold
                transition-all duration-200 hover:scale-105 active:scale-95
                ${language === "ur"
                  ? "border-primary bg-primary text-primary-foreground shadow-sm"
                  : "border-border bg-muted text-foreground hover:border-primary hover:bg-primary/5 hover:text-primary"
                }
              `}
            >
              <Languages className="w-3.5 h-3.5 shrink-0" />
              <span
                className={language === "ur" ? "font-noto" : ""}
                style={language === "ur" ? { fontFamily: "'Noto Nastaliq Urdu', serif" } : {}}
              >
                {t("langToggleLabel")}
              </span>
            </button>

            <Button size="sm" asChild>
              <Link to="/login">{t("navDashboard")}</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1">{children}</main>

      {/* Floating Chat Assistant on Home Page only */}
      {location.pathname === "/" && <ChatAssistant />}

      {/* Footer */}
      <footer className="border-t border-border bg-card">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid md:grid-cols-4 gap-10">
            {/* Brand + Description */}
            <div className="md:col-span-1 space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Leaf className="w-5 h-5 text-primary" />
                </div>
                <span className="text-lg font-bold text-foreground">{t("appName")}</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {language === "ur"
                  ? "ڈیٹا پر مبنی فصل نگرانی کا حل۔ IoT اور AI ٹولز کا استعمال کرتے ہوئے اپنے فارم کو خودکار بنائیں۔"
                  : "Data-driven crop monitoring solution. Automatize your farm by integrating data above and below ground using IoT and AI-based tools."}
              </p>
              {/* Social Icons */}
              <div className="flex gap-3 pt-2">
                {[
                  { icon: Facebook, href: "#" },
                  { icon: Instagram, href: "#" },
                  { icon: Linkedin, href: "#" },
                  { icon: Youtube, href: "#" },
                ].map((social, i) => (
                  <a
                    key={i}
                    href={social.href}
                    className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
                  >
                    <social.icon className="w-4 h-4" />
                  </a>
                ))}
              </div>
            </div>

            {/* Quick Links */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">
                {language === "ur" ? "فوری لنکس" : "Quick Links"}
              </h3>
              <div className="flex flex-col gap-2">
                {navLinks.map((link) => (
                  <Link
                    key={link.path}
                    to={link.path}
                    className="text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>

            {/* Contact Info */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">
                {language === "ur" ? "ہم سے رابطہ کریں" : "Get In Touch"}
              </h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <MapPin className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                  <span className="text-sm text-muted-foreground">
                    {language === "ur" ? "لاہور، پنجاب، پاکستان" : "Lahore, Punjab, Pakistan"}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="w-4 h-4 text-primary shrink-0" />
                  <span className="text-sm text-muted-foreground">+92 300 1234567</span>
                </div>
                <div className="flex items-center gap-3">
                  <Mail className="w-4 h-4 text-primary shrink-0" />
                  <span className="text-sm text-muted-foreground">support@agricheck.io</span>
                </div>
              </div>
            </div>

            {/* Newsletter */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">
                {language === "ur" ? "نیوز لیٹر" : "Newsletter"}
              </h3>
              <p className="text-sm text-muted-foreground">
                {language === "ur"
                  ? "پریسیژن زراعت میں تازہ ترین معلومات کے لیے سبسکرائب کریں۔"
                  : "Subscribe to stay updated with the latest in precision agriculture."}
              </p>
              <div className="flex gap-2">
                <input
                  type="email"
                  placeholder={language === "ur" ? "آپ کی ای میل" : "Your email"}
                  className="flex-1 px-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                <Button size="sm">
                  {language === "ur" ? "سبسکرائب" : "Subscribe"}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-border">
          <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-2">
            <p className="text-sm text-muted-foreground">
              &copy; {new Date().getFullYear()} {t("appName")}.{" "}
              {language === "ur" ? "تمام حقوق محفوظ ہیں۔" : "All rights reserved."}
            </p>
            <p className="text-sm text-muted-foreground">
              {language === "ur" ? "ایگری چیک کی طرف سے تقویت یافتہ" : "Powered by AgriCheck"}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
