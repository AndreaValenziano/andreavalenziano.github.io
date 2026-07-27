import { useState } from 'react'
import { trip } from '../data/trip'
import { euro, useStoredState } from '../lib/storage'
import { TrashIcon } from '../components/icons'
import type { Expense, NotesMap } from '../types'

const EXPENSE_CATEGORIES = ['Cibo', 'Ingressi e parcheggi', 'Carburante e pedaggi', 'Acquisti', 'Altro']

const DAY_OPTIONS: { value: string; label: string }[] = [
  { value: 'pre', label: 'Prima del viaggio' },
  ...trip.days.map((day) => ({
    value: day.date,
    label: `${day.weekday.slice(0, 3)} ${Number(day.date.slice(8))} agosto`,
  })),
]

const dayLabel = (value: string) => DAY_OPTIONS.find((option) => option.value === value)?.label ?? value

export function DiarioTab() {
  const [view, setView] = useState<'spese' | 'note'>('spese')

  return (
    <div className="space-y-4 px-4 pt-4 pb-6">
      <h1 className="font-display text-2xl font-semibold">Diario</h1>
      <div className="flex rounded-full bg-pietra-200/70 p-1 dark:bg-pietra-800">
        {(['spese', 'note'] as const).map((id) => (
          <button
            key={id}
            type="button"
            onClick={() => setView(id)}
            className={`min-h-10 flex-1 rounded-full text-sm font-semibold capitalize transition-colors ${
              view === id ? 'bg-pietra-50 shadow-sm dark:bg-pietra-950' : 'text-pietra-600 dark:text-pietra-300'
            }`}
          >
            {id === 'spese' ? '💶 Spese' : '📝 Note'}
          </button>
        ))}
      </div>
      {view === 'spese' ? <Expenses /> : <Notes />}
    </div>
  )
}

function Expenses() {
  const [expenses, setExpenses] = useStoredState<Expense[]>('expenses', [])
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [day, setDay] = useState(DAY_OPTIONS[1].value)
  const [category, setCategory] = useState('')

  const total = expenses.reduce((sum, e) => sum + e.amount, 0)
  const daysWithExpenses = DAY_OPTIONS.filter((option) => expenses.some((e) => e.day === option.value))

  const add = () => {
    const parsed = Number.parseFloat(amount.replace(',', '.'))
    const text = description.trim()
    if (!text || !Number.isFinite(parsed) || parsed <= 0) return
    setExpenses((prev) => [
      ...prev,
      { id: crypto.randomUUID(), description: text, amount: parsed, day, category: category || undefined },
    ])
    setDescription('')
    setAmount('')
    setCategory('')
  }

  return (
    <div className="space-y-4">
      <section className="rounded-2xl bg-gradient-to-br from-salvia-600 to-salvia-700 p-4 text-white shadow-sm">
        <p className="text-sm font-semibold text-salvia-100 uppercase">Totale complessivo</p>
        <p className="font-display mt-0.5 text-3xl font-bold">{euro.format(total)}</p>
        {daysWithExpenses.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {daysWithExpenses.map((option) => {
              const dayTotal = expenses.filter((e) => e.day === option.value).reduce((sum, e) => sum + e.amount, 0)
              return (
                <span key={option.value} className="rounded-full bg-white/15 px-2.5 py-1 text-xs font-semibold">
                  {option.label}: {euro.format(dayTotal)}
                </span>
              )
            })}
          </div>
        )}
      </section>

      <form
        className="space-y-2.5 rounded-2xl bg-pietra-50 p-4 shadow-sm dark:bg-pietra-900"
        onSubmit={(e) => {
          e.preventDefault()
          add()
        }}
      >
        <h2 className="font-display text-lg font-semibold">Aggiungi spesa</h2>
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Descrizione (es. pranzo, pedaggio…)"
          className="min-h-11 w-full rounded-xl border border-pietra-300 bg-white px-3 text-sm placeholder:text-pietra-400 dark:border-pietra-700 dark:bg-pietra-950"
        />
        <div className="flex gap-2.5">
          <input
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            inputMode="decimal"
            placeholder="Importo €"
            className="min-h-11 w-28 rounded-xl border border-pietra-300 bg-white px-3 text-sm placeholder:text-pietra-400 dark:border-pietra-700 dark:bg-pietra-950"
          />
          <select
            value={day}
            onChange={(e) => setDay(e.target.value)}
            className="min-h-11 min-w-0 flex-1 rounded-xl border border-pietra-300 bg-white px-2 text-sm dark:border-pietra-700 dark:bg-pietra-950"
          >
            {DAY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex gap-2.5">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="min-h-11 min-w-0 flex-1 rounded-xl border border-pietra-300 bg-white px-2 text-sm dark:border-pietra-700 dark:bg-pietra-950"
          >
            <option value="">Categoria (facoltativa)</option>
            {EXPENSE_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          <button
            type="submit"
            className="min-h-11 shrink-0 rounded-xl bg-terracotta-600 px-5 text-sm font-semibold text-white active:bg-terracotta-700"
          >
            Aggiungi
          </button>
        </div>
      </form>

      {daysWithExpenses.map((option) => (
        <section key={option.value} className="rounded-2xl bg-pietra-50 p-4 shadow-sm dark:bg-pietra-900">
          <h3 className="flex items-baseline justify-between text-sm font-bold tracking-wide text-terracotta-700 uppercase dark:text-terracotta-300">
            {option.label}
            <span className="font-display text-base text-pietra-900 normal-case dark:text-pietra-100">
              {euro.format(expenses.filter((e) => e.day === option.value).reduce((sum, e) => sum + e.amount, 0))}
            </span>
          </h3>
          <ul className="mt-2 space-y-1.5">
            {expenses
              .filter((e) => e.day === option.value)
              .map((expense) => (
                <li key={expense.id} className="flex items-center gap-2 text-sm">
                  <span className="min-w-0 flex-1">
                    {expense.description}
                    {expense.category && (
                      <span className="ml-1.5 text-xs text-pietra-500 dark:text-pietra-400">· {expense.category}</span>
                    )}
                  </span>
                  <span className="shrink-0 font-semibold">{euro.format(expense.amount)}</span>
                  <button
                    type="button"
                    onClick={() => setExpenses((prev) => prev.filter((e) => e.id !== expense.id))}
                    aria-label={`Elimina spesa «${expense.description}»`}
                    className="shrink-0 p-1 text-pietra-400 active:text-terracotta-600"
                  >
                    <TrashIcon className="size-4.5" />
                  </button>
                </li>
              ))}
          </ul>
        </section>
      ))}

      {expenses.length === 0 && (
        <p className="px-2 text-sm text-pietra-500 italic dark:text-pietra-400">
          Nessuna spesa registrata. Le spese restano salvate sul telefono anche offline.
        </p>
      )}
    </div>
  )
}

function Notes() {
  const [notes, setNotes] = useStoredState<NotesMap>('notes', {})
  const [selected, setSelected] = useState('pre')

  return (
    <div className="space-y-3">
      <div className="no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4">
        {DAY_OPTIONS.map((option) => {
          const hasText = Boolean(notes[option.value]?.trim())
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => setSelected(option.value)}
              className={`min-h-11 shrink-0 rounded-full px-4 text-sm font-semibold transition-colors ${
                selected === option.value
                  ? 'bg-terracotta-600 text-white'
                  : 'bg-pietra-200/70 text-pietra-700 dark:bg-pietra-800 dark:text-pietra-200'
              }`}
            >
              {option.value === 'pre' ? 'Generale' : option.label}
              {hasText && ' ·'}
            </button>
          )
        })}
      </div>
      <textarea
        value={notes[selected] ?? ''}
        onChange={(e) => setNotes((prev) => ({ ...prev, [selected]: e.target.value }))}
        rows={12}
        placeholder={`Note per «${selected === 'pre' ? 'Generale' : dayLabel(selected)}»…`}
        className="w-full rounded-2xl border border-pietra-300 bg-pietra-50 p-4 text-sm leading-relaxed placeholder:text-pietra-400 dark:border-pietra-700 dark:bg-pietra-900"
      />
      <p className="px-2 text-xs text-pietra-500 dark:text-pietra-400">
        Salvataggio automatico sul telefono, anche offline.
      </p>
    </div>
  )
}
