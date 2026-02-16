---

## 🧩 Phrase TMS ↔ GitHub Automation Workflow

[![Sync from Client Repo](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/sync-from-client-repo.yml/badge.svg)](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/sync-from-client-repo.yml)

[![AsciiDoc Preprocess](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/preprocess.yml/badge.svg)](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/preprocess.yml)

[![Process Phrase Incoming Files](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/pull-from-phrase-incoming.yml/badge.svg)](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/pull-from-phrase-incoming.yml)

[![AsciiDoc Postprocess](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/postprocess.yml/badge.svg)](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/postprocess.yml)

[![Sync to Client Repo](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/sync-to-client-repo.yml/badge.svg)](https://github.com/eoinmurphy-vt/suse.phrase.auto.multi.repo/actions/workflows/sync-to-client-repo.yml)

### 🔄 Overview

This repository is integrated with **Phrase TMS** to fully automate the translation lifecycle of AsciiDoc files.
It ensures consistent formatting, automatic preprocessing before translation, and automatic restoration afterward.

---

### ⚙️ Folder Structure

| Folder                  | Purpose                                                                        |
| ----------------------- | ------------------------------------------------------------------------------ |
| **`source/`**           | Original AsciiDoc files before translation                                     |
| **`processed/`**        | Preprocessed UTF-8 files prepared for Phrase TMS                               |
| **`phrase-incoming/`**  | Branch where Phrase TMS commits completed translations                         |
| **`translated/`**       | Folder where GitHub commits completed translations from phrase-incoming branch |
| **`final/`**            | Final postprocessed files restored to original AsciiDoc format                 |

---

### 🧠 Automation Logic

1. **Preprocessing Stage**

   * Trigger: when `.adoc` files are pushed to the `source/` folder
   * Converts files to UTF-8
   * Changes *Simple Monospaced* → *Literal Monospaced* formatting

     * Examples:

       ```adoc
       `.NET Library System.Formats.Abcd` → `+.NET Library System.Formats.Abcd+`
       ```
       ```adoc
       Select "`Next`" to continue. → Select &quot;`+Next+`&quot; to continue.
       ```
   * Converts `[monospaced]#text#` → `[literal]#text#`
   * Saves results in `processed/` for Phrase TMS to pull

2. **Translation Stage (in Phrase TMS)**

   * Phrase TMS syncs the `processed/` folder as the **source**
   * Machine translation is applied directly in Phrase TMS
   * When translation is complete, Phrase TMS pushes the files to the `translated/` folder in GitHub

3. **Postprocessing Stage**

   * Trigger: when `.adoc` files are pushed to the `translated/` folder
   * Reverts all preprocessing changes so files match the original AsciiDoc style

     * Examples:

       ```adoc
       `+.NET Library System.Formats.Abcd+` → `.NET Library System.Formats.Abcd`
       ```
       ```adoc
       Select &quot;`+Next+`&quot; to continue. → Select "`Next`" to continue.
       ```
   * Converts `[literal]#text#` → `[monospaced]#text#`
   * Force all `AsciiDoc files` to use `Unix LF` newlines
   * Writes clean, final files into the `final/` folder

---

### 🚦 Automation Status

The badges above show the current automation state for each workflow action:

| Status         | Meaning                                                                    |
| -------------- | -------------------------------------------------------------------------- |
| 🟢 **Passing** | The most recent preprocessing or postprocessing job completed successfully |
| 🔴 **Failing** | The workflow encountered an error — check the *Actions* tab for logs       |

---

### 📂 Repository Structure

Ensure your project follows this structure to support the scripts:

    ├── source/                    # Source English files
    ├── processed/                 # Pre-processed English files
    ├── translated/                # Translated files
    ├── final/                     # Post-processed translated files
    ├── logs/                      # Execution logs
    ├── .github/
    │   └── workflows/
    │       ├── sync-from-client-repo.yml        # Triggered on push to main
    │       ├── preprocess.yml                   # Triggered on phrase updates
    │       ├── pull-from-phrase-incoming.yml    # Triggered on push to main
    │       ├── postprocess.yml                  # Triggered on push to main
    │       ├── sync-to-client-repo.yml          # Triggered on phrase updates
    │       └── clean_workflow.yml               # Triggered manually
    ├── preprocess_adoc.py         # The Protection Script
    └── postprocess_adoc.py        # The Restoration Script

---

### 👥 For Translators and Project Managers

* Upload or commit new `.adoc` files to the **`source/`** folder.
* Phrase TMS will automatically detect and import them from the **`processed/`** folder.
* Once translations are complete, the **`translated/`** folder will be updated automatically.
* Within a few minutes, the **`final/`** folder will contain the finalized AsciiDoc files, fully restored and ready for publication.

---

### ⚙️ Configuration & Admin Guide

This workflow uses GitHub Actions Variables to manage repository connections and folder paths. This allows administrators to change configuration (like switching to a new target repository or changing folder names) without editing any code.

1. **How to Change Settings**

   * Navigate to the main page of this repository.
   * Click the Settings tab in the top navigation bar.
   * In the left sidebar, locate the Security section and Secrets and variables.
   * Click Actions.
   * Select the Variables tab (ensure you are not on the "Secrets" tab).
   * To change a setting, click the pencil icon (Edit) next to the variable.
   * To add a missing setting, click New repository variable.

2. **Available Variables**

If these variables are not set, the workflow will use the Default Values listed below.

| Variable Name                   | Default Value       | Description                                                                                                      |
| ------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **`CONTENT_DIR`**               | source              | The local folder where English .adoc files are stored.                                                           |
| **`TRANSLATED_DIR`**            | translated          | The folder where Phrase TMS pushes translated files.                                                             |
| **`FINAL_DIR`**                 | final               | The folder where the final, cleaned AsciiDoc files are saved.                                                    |
| **`PHRASE_INCOMING_BRANCH`**    | phrase-incoming     | The specific Branch where Phrase TMS commits completed translations.                                             |
| **`CURRENT_REPO_NAME`**         | (Your Repo)         | The owner/repo string of this repository (e.g., my-org/docs-connector). Used for dispatch triggers.              |
| **`SUSE_CLIENT_CONFIGURATION`** | (JSON content)      | The configuration settings used to connect to client repos (id, url, branch, schedule, watch_path, target_path). |

***

**Example: `SUSE_CLIENT_CONFIGURATION`**

This variable stores the client‑specific repository configuration in JSON format:

```json
{
  "id": "suse-repo-a",
  "url": "suse.client/suse.phrase.auto.repo.one",
  "branch": "main",
  "schedule": "hourly",
  "watch_path": "docs/modules/en/",
  "target_path": "docs/modules/"
}
```

**Field Descriptions**

| Field            | Meaning                                                         |
| ---------------- | --------------------------------------------------------------- |
| **id**           | Unique identifier for the client configuration.                 |
| **url**          | GitHub repository path in `owner/repo` format.                  |
| **branch**       | The branch monitored for updates.                               |
| **schedule**     | How often this repo should be pulled (`hourly`, `daily`, etc.). |
| **watch\_path**  | Path within the client repo to watch for changes.               |
| **target\_path** | Path in this repository where processed files are saved.        |

***

---

### ⚠️ Important Limitations

   While most settings are configurable via the Variables UI, specific GitHub architecture limitations require the following to be changed manually in the YML files if updated:
   * Schedules: The sync frequency (e.g., */15 * * * *) must be edited in .github/workflows/sync-from-repo1.yml.
   * Trigger Paths: If you rename the source or translated folders, you must manually update the paths: filters in preprocess.yml and postprocess.yml so the workflows trigger correctly.

---

### 🧩 Technical Notes

* Stages run via [GitHub Actions](https://github.com/features/actions).
* Scripts used:

  * `preprocess_adoc.py`
  * `postprocess_adoc.py`
* Encoding: **Unix-compatible UTF-8**
* Languages: **de-DE, es-ES, fr-FR, ja-JP, pt-BR, zh-CN**

---

### <img src="assets/phrase_icon.png" width="24" style="position: relative; top: 8px;" /> Phrase Integration

**Phrase GitHub App**

Install the `Phrase GitHub App` on your GitHub repository to enable sending files to Phrase TMS.

   * [Phrase GitHub App](https://github.com/apps/phrase-app-connector-eu)

**Connector**

In Phrase TMS set up a `Connector` to link to your GitHub repository.

   * Configure the pull request branch and the folder used for import/export.

**Project templates**

In Phrase TMS, configure `Project templates`.

   * Each language requires its own project template
   * Configure the machine translation engine
   * Configure pre-translation rules
   * Configure project status automation
   * Define completed file naming and export paths
   * Configure file import settings
   * Configure optional settings such as Analysis and Workflow

**Automated project creation**

In Phrase TMS set up `Automated project creation` templates.

   * Each language requires its own automation template
   * Select the project template to use
   * Configure export rules
   * Define the remote folders and file types that trigger automations
   * Configure trigger monitors (scheduled or webhook-based)
   * Configure any additional project actions

**Phrase Orchestrator**

In Phrase Orchestrator, set up a `Workflow`.

   * Add a filter to the workflow for each project template
   * The workflow is used to save completed translations to the project TM

---

### 📝 License

This project is licensed under the Apache 2.0 License. © 2026 Vistatec.

---