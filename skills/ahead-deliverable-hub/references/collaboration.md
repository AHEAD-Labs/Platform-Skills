# Working on one hub as a team

A hub is a single HTML file edited by several people over several weeks. These practices keep
edits from colliding and stop the package becoming a last-minute effort.

## The file

- Keep one master file in the engagement's SharePoint deliverables folder. Everyone edits that file.
- Name it `<Client> x AHEAD <Phase> <Package name>.html`. Let SharePoint version history track
  versions; if you also keep numbered copies, never overwrite a teammate's version.
- When Claude edits a file someone else has touched, it works on the **latest uploaded file** and
  changes only the slots it was asked to fill (`fill_slot.py`), saving a new version. It does not
  rebuild from the config, because a rebuild discards everyone's edits.

## Check out and check in (SharePoint)

1. Select the file in the SharePoint library, open the ... menu, choose **More > Check out**.
   The file now shows a red arrow and others can open but not save it.
2. Download it, edit your slots in a text editor, open it in a browser to check.
3. Upload it back to the same folder with the same name (choose **Replace**).
4. Select it, choose **More > Check in**, and add a one-line comment ("Filled Operating Model RACI").
5. If you finish without changes, choose **Discard check out**.

A library owner can turn on **Library settings > Versioning settings > Require check out** so nobody
can save without checking out first. If the team prefers not to use check-out, the fallback is a
short message in the team chat before and after editing ("Taking the hub for 30 minutes" / "Hub back").

## Cadence

- Each owner updates their sections at least **once a week** (a fixed day, for example Friday).
- The engagement lead reviews the `?check` view weekly: open the file with `?check` on the end of the
  address to list remaining placeholders by tab and by owner.
- Aim for **near-final early in the last week**, leaving time for a principal review, a style pass
  (`check.py`) and the client walkthrough.
- Before handover, run `check.py --final --client "<Client>"`; it fails if any placeholder remains.

## Ownership

- One owner per slot, shown on the placeholder with their initials. The contributor guide
  (`guide.py` output) lists each person's slots; regenerate it whenever owners change.
- The principal consultant owns the Overview and writes it last, from the finished tabs, with input
  from the engagement director on direction.
- Owners raise a structural change (a new section, a renamed tab) with the engagement lead rather
  than editing the structure in the file; the lead updates the config and rebuilds only while the
  file is still empty, or adds the slot by hand later.

## Announcing the template (Teams message)

Keep it short and in the sender's own voice. Adjust names and dates; a sender writing to more senior
colleagues should frame it as their approach and invite comment. Example:

> Hi all, here is the draft template for the <Phase> deliverable package: <link>.
> Each section is tagged with its owner, so you can see where your content goes.
> To edit, check the file out in SharePoint, make your changes, then check it back in, so we avoid
> overwriting each other.
> Please update your sections at least once a week, so we are close to final early in Week <n> rather
> than at the end. Happy to walk through the structure in <meeting>.

## Before sharing with the client

- `check.py --final --client "<Client>"` passes (no placeholders, no broken links, no team names).
- Visual check of every tab at laptop width (1280 to 1440 px) and on a narrow window.
- Principal review of the Overview against the finished tabs.
- Remove any internal-only commentary; the HTML comment at the top of the file (the editing guide)
  can stay, as it is invisible to readers, or be removed at the user's request.
