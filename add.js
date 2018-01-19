// 普通のやりかた
const add = (a, b) => console.log(a + b)

add(2, 3)


console.log('-----------------------------')

// Producer + Consumer パターン
tasks = { add }
aries = []

const produce = (ary) => aries.push(ary)

const consume = () => {
  if (aries.length === 0) {
    return
  }
  const ary = aries.shift()
  const rest = ary.splice(1)
  tasks[ary[0]](...rest)
}

produce(['add', 2, 3])
produce(['add', 3, 4])
consume()
consume()
consume()
consume()
consume()
produce(['add', 4, 14])
consume()
consume()
produce(['add', 4, 14])
produce(['add', 4, 14])
