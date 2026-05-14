import { useState } from "react";
import { Settings, AlertCircle, CheckCircle, Eye, EyeOff, Loader2 } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function SettingsPage() {
  const { t } = useLanguage();
  const { user, updateUsername, updateUserEmail, updateUserPassword } = useAuth();

  // Form states
  const [usernameForm, setUsernameForm] = useState({ name: user?.name || "", isEditing: false });
  const [emailForm, setEmailForm] = useState({ email: "", password: "", isEditing: false });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
    isEditing: false,
    showPasswords: false,
  });

  // Status states
  const [usernameStatus, setUsernameStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });

  const [emailStatus, setEmailStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });

  const [passwordStatus, setPasswordStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });

  // Update Username Handler
  const handleUpdateUsername = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!usernameForm.name.trim()) {
      setUsernameStatus({ type: "error", message: t("usernameCannotBeEmpty") });
      return;
    }

    try {
      setUsernameStatus({ type: "loading", message: t("saving") });
      await updateUsername(usernameForm.name);
      setUsernameStatus({ type: "success", message: t("usernameUpdatedSuccess") });
      setUsernameForm({ ...usernameForm, isEditing: false });
      setTimeout(() => setUsernameStatus({ type: "idle", message: "" }), 3000);
    } catch (err) {
      setUsernameStatus({
        type: "error",
        message: err instanceof Error ? err.message : t("failedToFetchData"),
      });
    }
  };

  // Update Email Handler
  const handleUpdateEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailForm.email.trim() || !emailForm.password.trim()) {
      setEmailStatus({ type: "error", message: t("emailPasswordRequired") });
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailForm.email)) {
      setEmailStatus({ type: "error", message: t("invalidEmailFormat") });
      return;
    }

    try {
      setEmailStatus({ type: "loading", message: t("saving") });
      await updateUserEmail(emailForm.password, emailForm.email);
      setEmailStatus({ type: "success", message: t("emailUpdatedSuccess") });
      setEmailForm({ email: "", password: "", isEditing: false });
      setTimeout(() => setEmailStatus({ type: "idle", message: "" }), 3000);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to update email";
      setEmailStatus({
        type: "error",
        message: errorMsg.includes("auth/wrong-password")
          ? t("incorrectPassword")
          : errorMsg.includes("auth/email-already-in-use")
            ? t("emailAlreadyInUse")
            : errorMsg,
      });
    }
  };

  // Update Password Handler
  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!passwordForm.currentPassword.trim()) {
      setPasswordStatus({ type: "error", message: t("currentPasswordRequired") });
      return;
    }

    if (passwordForm.newPassword.length < 6) {
      setPasswordStatus({ type: "error", message: t("passwordMin6Chars") });
      return;
    }

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPasswordStatus({ type: "error", message: t("passwordsDoNotMatch") });
      return;
    }

    if (passwordForm.currentPassword === passwordForm.newPassword) {
      setPasswordStatus({
        type: "error",
        message: t("passwordMustBeDifferent"),
      });
      return;
    }

    try {
      setPasswordStatus({ type: "loading", message: t("saving") });
      await updateUserPassword(passwordForm.currentPassword, passwordForm.newPassword);
      setPasswordStatus({ type: "success", message: t("passwordUpdatedSuccess") });
      setPasswordForm({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
        isEditing: false,
        showPasswords: false,
      });
      setTimeout(() => setPasswordStatus({ type: "idle", message: "" }), 3000);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to update password";
      setPasswordStatus({
        type: "error",
        message: errorMsg.includes("auth/wrong-password")
          ? t("incorrectCurrentPassword")
          : errorMsg,
      });
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6 lg:space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start sm:items-center gap-2 sm:gap-3 mb-4 sm:mb-6 px-0.5">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
            <Settings className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg sm:text-2xl lg:text-3xl font-bold text-foreground">{t("settingsHeading")}</h1>
            <p className="text-xs sm:text-sm text-muted-foreground">{t("settingsSubheading")}</p>
          </div>
        </div>
      </motion.div>

      {/* User Info Display */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-base sm:text-lg">{t("accountInformation")}</CardTitle>
            <CardDescription className="text-xs sm:text-sm">{t("currentlyLoggedInAs")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 sm:space-y-4">
            <div>
              <p className="text-xs sm:text-sm font-semibold text-muted-foreground">{t("name")}</p>
              <p className="text-base sm:text-lg text-foreground truncate">{user?.name}</p>
            </div>
            <div>
              <p className="text-xs sm:text-sm font-semibold text-muted-foreground">{t("email")}</p>
              <p className="text-base sm:text-lg text-foreground truncate">{user?.email}</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Update Username */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-base sm:text-lg">{t("updateUsername")}</CardTitle>
            <CardDescription className="text-xs sm:text-sm">{t("changeDisplayName")}</CardDescription>
          </CardHeader>
          <CardContent>
            {usernameStatus.type !== "idle" && (
              <Alert variant={usernameStatus.type === "error" ? "destructive" : "default"} className="mb-4">
                {usernameStatus.type === "error" ? (
                  <AlertCircle className="h-4 w-4" />
                ) : (
                  <CheckCircle className="h-4 w-4" />
                )}
                <AlertDescription>{usernameStatus.message}</AlertDescription>
              </Alert>
            )}

            {!usernameForm.isEditing ? (
              <Button onClick={() => setUsernameForm({ ...usernameForm, isEditing: true })} variant="outline">
                {t("editUsername")}
              </Button>
            ) : (
              <form onSubmit={handleUpdateUsername} className="space-y-4">
                <div>
                  <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                    {t("newUsername")}
                  </label>
                  <Input
                    type="text"
                    value={usernameForm.name}
                    onChange={(e) => setUsernameForm({ ...usernameForm, name: e.target.value })}
                    placeholder={t("enterNewUsername")}
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={usernameStatus.type === "loading"}>
                    {usernameStatus.type === "loading" ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {t("saving")}
                      </>
                    ) : (
                      t("save")
                    )}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setUsernameForm({ ...usernameForm, isEditing: false, name: user?.name || "" });
                      setUsernameStatus({ type: "idle", message: "" });
                    }}
                    disabled={usernameStatus.type === "loading"}
                  >
                    {t("cancel")}
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Update Email */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{t("updateEmail")}</CardTitle>
            <CardDescription>{t("changeEmailAddress")}</CardDescription>
          </CardHeader>
          <CardContent>
            {emailStatus.type !== "idle" && (
              <Alert variant={emailStatus.type === "error" ? "destructive" : "default"} className="mb-4">
                {emailStatus.type === "error" ? (
                  <AlertCircle className="h-4 w-4" />
                ) : (
                  <CheckCircle className="h-4 w-4" />
                )}
                <AlertDescription>{emailStatus.message}</AlertDescription>
              </Alert>
            )}

            {!emailForm.isEditing ? (
              <Button onClick={() => setEmailForm({ ...emailForm, isEditing: true })} variant="outline">
                {t("editEmail")}
              </Button>
            ) : (
              <form onSubmit={handleUpdateEmail} className="space-y-4">
                <div>
                  <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                    {t("newEmail")}
                  </label>
                  <Input
                    type="email"
                    value={emailForm.email}
                    onChange={(e) => setEmailForm({ ...emailForm, email: e.target.value })}
                    placeholder={t("enterNewEmail")}
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                    {t("currentPasswordVerification")}
                  </label>
                  <Input
                    type="password"
                    value={emailForm.password}
                    onChange={(e) => setEmailForm({ ...emailForm, password: e.target.value })}
                    placeholder={t("enterYourPassword")}
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={emailStatus.type === "loading"}>
                    {emailStatus.type === "loading" ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {t("saving")}
                      </>
                    ) : (
                      t("save")
                    )}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setEmailForm({ email: "", password: "", isEditing: false });
                      setEmailStatus({ type: "idle", message: "" });
                    }}
                    disabled={emailStatus.type === "loading"}
                  >
                    {t("cancel")}
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Update Password */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{t("updatePassword")}</CardTitle>
            <CardDescription>{t("changeAccountPassword")}</CardDescription>
          </CardHeader>
          <CardContent>
            {passwordStatus.type !== "idle" && (
              <Alert variant={passwordStatus.type === "error" ? "destructive" : "default"} className="mb-4">
                {passwordStatus.type === "error" ? (
                  <AlertCircle className="h-4 w-4" />
                ) : (
                  <CheckCircle className="h-4 w-4" />
                )}
                <AlertDescription>{passwordStatus.message}</AlertDescription>
              </Alert>
            )}

            {!passwordForm.isEditing ? (
              <Button onClick={() => setPasswordForm({ ...passwordForm, isEditing: true })} variant="outline">
                {t("editPassword")}
              </Button>
            ) : (
              <form onSubmit={handleUpdatePassword} className="space-y-4">
                <div className="relative">
                  <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                    {t("currentPassword")}
                  </label>
                  <div className="relative">
                    <Input
                      type={passwordForm.showPasswords ? "text" : "password"}
                      value={passwordForm.currentPassword}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, currentPassword: e.target.value })
                      }
                      placeholder="Enter current password"
                    />
                  </div>
                </div>

                <div className="relative">
                  <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                    {t("newPassword")}
                  </label>
                  <div className="relative">
                    <Input
                      type={passwordForm.showPasswords ? "text" : "password"}
                      value={passwordForm.newPassword}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, newPassword: e.target.value })
                      }
                      placeholder="Enter new password"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {t("min6Chars")}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                    {t("confirmNewPassword")}
                  </label>
                  <div className="relative">
                    <Input
                      type={passwordForm.showPasswords ? "text" : "password"}
                      value={passwordForm.confirmPassword}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })
                      }
                      placeholder="Confirm new password"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setPasswordForm({ ...passwordForm, showPasswords: !passwordForm.showPasswords })
                      }
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {passwordForm.showPasswords ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button type="submit" disabled={passwordStatus.type === "loading"}>
                    {passwordStatus.type === "loading" ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {t("saving")}
                      </>
                    ) : (
                      t("save")
                    )}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setPasswordForm({
                        currentPassword: "",
                        newPassword: "",
                        confirmPassword: "",
                        isEditing: false,
                        showPasswords: false,
                      });
                      setPasswordStatus({ type: "idle", message: "" });
                    }}
                    disabled={passwordStatus.type === "loading"}
                  >
                    {t("cancel")}
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
