import i18n from "i18next";
import { initReactI18next } from "react-i18next";

export const supportedLocales = ["pt-BR", "en-US"] as const;

const resources = {
  "en-US": {
    translation: {
      workspace: {
        activity: "Activity",
        admin: "Admin",
        ai: "AI assistance",
        apiHealth: "API health",
        attention: "Attention",
        commandCenter: "Command center",
        commandCenterDescription:
          "Project navigation, runtime state, lifecycle actions, preferences, audit, and AI review are available through focused workspace sections.",
        connectedAs: "Connected as",
        guestTitle: "OrchFlow",
        lifecycleHealth: "Lifecycle health",
        noSelection: "No project selected",
        overview: "Overview",
        preferencesError: "Preferences need attention",
        preferencesRefresh: "Refresh",
        preferencesSaved: "Preferences saved.",
        preferencesSaving: "Saving...",
        preferencesSave: "Save preferences",
        preferencesStatusRefreshInterval: "Status refresh interval",
        preferencesProjectDisplay: "Project display",
        preferencesTable: "Table",
        preferencesList: "List",
        preferencesLanguage: "Language",
        preferencesEnglish: "English (US)",
        preferencesPortuguese: "Portuguese (Brazil)",
        preferencesTitle: "User display settings",
        preferencesWorkspace: "Workspace preferences",
        profile: "Profile",
        projects: "Projects",
        refresh: "Refresh",
        running: "Running",
        settings: "Settings",
        signOut: "Sign out",
        system: "System",
        tools: "Tools",
        unknown: "unknown",
        workspace: "Workspace",
      },
    },
  },
  "pt-BR": {
    translation: {
      workspace: {
        activity: "Atividade",
        admin: "Administração",
        ai: "Assistência de IA",
        apiHealth: "Saúde da API",
        attention: "Atenção",
        commandCenter: "Centro de comando",
        commandCenterDescription:
          "Navegação de projetos, estado de execução, ações de ciclo de vida, preferências, auditoria e revisão de IA estão disponíveis em seções focadas do espaço de trabalho.",
        connectedAs: "Conectado como",
        guestTitle: "OrchFlow",
        lifecycleHealth: "Saúde do ciclo de vida",
        noSelection: "Nenhum projeto selecionado",
        overview: "Visão geral",
        preferencesError: "As preferências exigem atenção",
        preferencesRefresh: "Atualizar",
        preferencesSaved: "Preferências salvas.",
        preferencesSaving: "Salvando...",
        preferencesSave: "Salvar preferências",
        preferencesStatusRefreshInterval: "Intervalo de atualização de status",
        preferencesProjectDisplay: "Exibição de projetos",
        preferencesTable: "Tabela",
        preferencesList: "Lista",
        preferencesLanguage: "Idioma",
        preferencesEnglish: "Inglês (EUA)",
        preferencesPortuguese: "Português (Brasil)",
        preferencesTitle: "Configurações de exibição",
        preferencesWorkspace: "Preferências do espaço de trabalho",
        profile: "Perfil",
        projects: "Projetos",
        refresh: "Atualizar",
        running: "Em execução",
        settings: "Configurações",
        signOut: "Sair",
        system: "Sistema",
        tools: "Ferramentas",
        unknown: "desconhecido",
        workspace: "Espaço de trabalho",
      },
    },
  },
} as const;

void i18n.use(initReactI18next).init({
  fallbackLng: "en-US",
  interpolation: { escapeValue: false },
  lng: "pt-BR",
  resources,
  supportedLngs: supportedLocales,
});

export default i18n;
