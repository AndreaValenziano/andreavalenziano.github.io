import { useState } from 'react'
import { CHECKLIST_CATEGORIES, initialChecklist } from '../data/checklist'
import { useStoredState } from '../lib/storage'
import { PencilIcon, PlusIcon, TrashIcon } from '../components/icons'
import type { ChecklistCategory, ChecklistItem } from '../types'

export function ChecklistTab() {
  const [items, setItems] = useStoredState<ChecklistItem[]>('checklist', initialChecklist)

  const toggle = (id: string) =>
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, done: !item.done } : item)))
  const remove = (id: string) => setItems((prev) => prev.filter((item) => item.id !== id))
  const rename = (id: string, text: string) =>
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, text } : item)))
  const add = (category: ChecklistCategory, text: string) =>
    setItems((prev) => [...prev, { id: crypto.randomUUID(), category, text, done: false }])

  return (
    <div className="space-y-4 px-4 pt-4 pb-6">
      <h1 className="font-display text-2xl font-semibold">Checklist</h1>
      {CHECKLIST_CATEGORIES.map((category) => {
        const categoryItems = items.filter((item) => item.category === category.id)
        const doneCount = categoryItems.filter((item) => item.done).length
        return (
          <section key={category.id} className="rounded-2xl bg-pietra-50 p-4 shadow-sm dark:bg-pietra-900">
            <header className="flex items-baseline justify-between gap-2">
              <h2 className="font-display text-lg font-semibold">
                <span aria-hidden="true">{category.emoji}</span> {category.label}
              </h2>
              {categoryItems.length > 0 && (
                <span
                  className={`text-sm font-bold ${
                    doneCount === categoryItems.length
                      ? 'text-salvia-600 dark:text-salvia-300'
                      : 'text-pietra-500 dark:text-pietra-400'
                  }`}
                >
                  {doneCount}/{categoryItems.length}
                </span>
              )}
            </header>
            <ul className="mt-3 space-y-1">
              {categoryItems.map((item) => (
                <ChecklistRow
                  key={item.id}
                  item={item}
                  onToggle={() => toggle(item.id)}
                  onRemove={() => remove(item.id)}
                  onRename={(text) => rename(item.id, text)}
                />
              ))}
              {categoryItems.length === 0 && (
                <li className="py-2 text-sm text-pietra-500 italic dark:text-pietra-400">
                  Nessuna voce: aggiungine una qui sotto.
                </li>
              )}
            </ul>
            <AddItemForm onAdd={(text) => add(category.id, text)} />
          </section>
        )
      })}
    </div>
  )
}

function ChecklistRow({
  item,
  onToggle,
  onRemove,
  onRename,
}: {
  item: ChecklistItem
  onToggle: () => void
  onRemove: () => void
  onRename: (text: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(item.text)

  const save = () => {
    const text = draft.trim()
    if (text) onRename(text)
    else setDraft(item.text)
    setEditing(false)
  }

  if (editing) {
    return (
      <li className="flex items-center gap-2 py-1">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && save()}
          autoFocus
          className="min-h-11 w-full flex-1 rounded-xl border border-pietra-300 bg-white px-3 text-sm dark:border-pietra-700 dark:bg-pietra-950"
        />
        <button
          type="button"
          onClick={save}
          className="min-h-11 shrink-0 rounded-full bg-terracotta-600 px-4 text-sm font-semibold text-white"
        >
          OK
        </button>
      </li>
    )
  }

  return (
    <li className="group flex items-start gap-2.5 py-1">
      <button
        type="button"
        role="checkbox"
        aria-checked={item.done}
        onClick={onToggle}
        className={`mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-lg border-2 transition-colors ${
          item.done
            ? 'border-salvia-500 bg-salvia-500 text-white'
            : 'border-pietra-400 bg-transparent dark:border-pietra-600'
        }`}
      >
        {item.done && (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" className="size-4" aria-hidden="true">
            <path d="m5 12.5 4.5 4.5L19 7.5" />
          </svg>
        )}
      </button>
      <button
        type="button"
        onClick={onToggle}
        className={`min-w-0 flex-1 py-0.5 text-left text-sm leading-relaxed ${
          item.done ? 'text-pietra-400 line-through dark:text-pietra-500' : ''
        }`}
      >
        {item.text}
      </button>
      <button
        type="button"
        onClick={() => {
          setDraft(item.text)
          setEditing(true)
        }}
        aria-label={`Modifica «${item.text}»`}
        className="mt-0.5 shrink-0 p-1 text-pietra-400 active:text-terracotta-600"
      >
        <PencilIcon className="size-4.5" />
      </button>
      <button
        type="button"
        onClick={onRemove}
        aria-label={`Elimina «${item.text}»`}
        className="mt-0.5 shrink-0 p-1 text-pietra-400 active:text-terracotta-600"
      >
        <TrashIcon className="size-4.5" />
      </button>
    </li>
  )
}

function AddItemForm({ onAdd }: { onAdd: (text: string) => void }) {
  const [text, setText] = useState('')

  const submit = () => {
    const value = text.trim()
    if (!value) return
    onAdd(value)
    setText('')
  }

  return (
    <form
      className="mt-3 flex gap-2"
      onSubmit={(e) => {
        e.preventDefault()
        submit()
      }}
    >
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Aggiungi voce…"
        className="min-h-11 w-full flex-1 rounded-xl border border-pietra-300 bg-white px-3 text-sm placeholder:text-pietra-400 dark:border-pietra-700 dark:bg-pietra-950"
      />
      <button
        type="submit"
        aria-label="Aggiungi voce"
        className="flex min-h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-terracotta-600 text-white active:bg-terracotta-700"
      >
        <PlusIcon className="size-5" />
      </button>
    </form>
  )
}
