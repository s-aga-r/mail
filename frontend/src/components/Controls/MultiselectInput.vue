<template>
<div>
    <div class="flex flex-wrap gap-1">
        <Button
            ref="emails"
            v-for="value in values"
            :key="value"
            :label="value"
            theme="gray"
            variant="subtle"
            class="rounded text-sm"
            @keydown.delete.capture.stop="removeLastValue"
        >
            <template #suffix>
            <X
                class="h-3.5"
                name="x"
                @click.stop="removeValue(value)"
            />
            </template>
        </Button>
        <div class="flex-1">
            <Combobox v-model="selectedValue" nullable>
                <Popover class="w-full" v-model:show="showOptions">
                    <template #target="{ togglePopover }">
                        <ComboboxInput
                            ref="search"
                            class="search-input form-input w-full border-none bg-white hover:bg-white focus:border-none focus:!shadow-none focus-visible:!ring-0"
                            type="text"
                            :value="query"
                            @change="
                            (e) => {
                                query = e.target.value
                                showOptions = true
                            }
                            "
                            @keydown.enter="() => addValue(query)"
                            autocomplete="off"
                            @focus="() => togglePopover()"
                            @keydown.delete.capture.stop="removeLastValue"
                        />
                        </template>
                        <template #body="{ isOpen }">
                        <div v-show="isOpen">
                            <div v-if="options.length" class="mt-1 rounded-lg bg-white py-1 text-sm shadow-2xl">
                                <ComboboxOptions
                                    class="my-1 max-h-[12rem] overflow-y-auto px-1.5"
                                    static
                                >
                                    <ComboboxOption
                                        v-for="option in options"
                                        :key="option.value"
                                        :value="option"
                                        v-slot="{ active }"
                                        >
                                        <li
                                            :class="[
                                            'flex cursor-pointer items-center rounded px-2 py-1 text-base',
                                            { 'bg-gray-100': active },
                                            ]"
                                        >
                                            <Avatar
                                            class="mr-2"
                                            :label="option.value"
                                            :image="option.image"
                                            size="lg"
                                            />
                                            <div class="flex flex-col gap-1 p-1 text-gray-800">
                                                <div class="text-sm font-medium">
                                                    {{ option.label }}
                                                </div>
                                                <div class="text-sm text-gray-600">
                                                    {{ option.value }}
                                                </div>
                                            </div>
                                        </li>
                                    </ComboboxOption>
                                </ComboboxOptions>
                            </div>
                        </div>
                    </template>
                </Popover>
            </Combobox>
        </div>
    </div>
    <ErrorMessage class="mt-2 pl-2" v-if="error" :message="error" />
</div>
</template>

<script setup>
import {
Combobox,
ComboboxInput,
ComboboxOptions,
ComboboxOption,
} from '@headlessui/vue'
import { createResource, Button, ErrorMessage } from 'frappe-ui'
import { ref, computed, nextTick } from 'vue'
import { watchDebounced } from '@vueuse/core'
import { Popover, Avatar } from 'frappe-ui'
import { X } from 'lucide-vue-next'

const props = defineProps({
    validate: {
        type: Function,
        default: null,
    },
    errorMessage: {
        type: Function,
        default: (value) => `${value} is an Invalid value`,
    },
})

const values = defineModel()

const emails = ref([])
const search = ref(null)
const error = ref(null)
const query = ref('')
const text = ref('')
const showOptions = ref(false)

const selectedValue = computed({
get: () => query.value || '',
set: (val) => {
    query.value = ''
    if (val) {
        showOptions.value = false
    }
    val?.value && addValue(val.value)
},
})

watchDebounced(
    query,
    (val) => {
        val = val || ''
        if (text.value === val && options.value?.length) return
        text.value = val
        reload(val)
    },
    { debounce: 300, immediate: true },
)

const filterOptions = createResource({
    url: 'mail.api.mail.get_mail_contacts',
    makeParams(values) {
        return {
            txt: values.txt,
        }
    },
    transform: (data) => {
        let allData = data
        .map((option) => {
            let fullName = option["full_name"]
            let email = option["email"]
            let name = option["email"]
            return {
                label: fullName || name || email,
                value: email,
                image: option["user_image"],
            }
        })
        return allData
    },
})

const options = computed(() => {
    let searchedContacts = filterOptions.data || []
    if (!searchedContacts.length && query.value) {
        searchedContacts.push({
            label: query.value,
            value: query.value,
        })
    }
    return searchedContacts
})

function reload(val) {
    filterOptions.reload({
        txt: val,
    })
}

const addValue = (value) => {
    error.value = null
    if (value) {
        const splitValues = value.split(',')
        splitValues.forEach((value) => {
        value = value.trim()
        if (value) {
            // check if value is not already in the values array
            if (!values.value?.includes(value)) {
            // check if value is valid
            if (value && props.validate && !props.validate(value)) {
                error.value = props.errorMessage(value)
                return
            }
            // add value to values array
            if (!values.value) {
                values.value = [value]
            } else {
                values.value.push(value)
            }
            value = value.replace(value, '')
            }
        }
        })
        !error.value && (value = '')
    }
}

const removeValue = (value) => {
    values.value = values.value.filter((v) => v !== value)
}

const removeLastValue = () => {
if (query.value) return

let emailRef = emails.value[emails.value.length - 1]?.$el
    if (document.activeElement === emailRef) {
        values.value.pop()
        nextTick(() => {
        if (values.value.length) {
            emailRef = emails.value[emails.value.length - 1].$el
            emailRef?.focus()
        } else {
            setFocus()
        }
        })
    } else {
        emailRef?.focus()
    }
}

function setFocus() {
    search.value.$el.focus()
}

defineExpose({ setFocus })
</script>
