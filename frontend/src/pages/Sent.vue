<template>
    <div class="h-full">
        <header class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-3 py-2.5 sm:px-5">
            <Breadcrumbs :items="breadcrumbs">
                <template #suffix>
                    <div v-if="outgoingMailCount.data" class="self-end text-xs text-gray-600 ml-2">
                        {{ __('{0} {1}').format(formatNumber(outgoingMailCount.data), outgoingMailCount.data == 1 ? singularize('messages') : 'messages') }}
                    </div>
                </template>
            </Breadcrumbs>
            <HeaderActions />
        </header>
        <div v-if="outgoingMails.data" class="flex h-[calc(100vh-3.2rem)]">
            <div @scroll="loadMoreEmails" ref="mailSidebar"
                class="mailSidebar border-r w-1/3 p-2 sticky top-16 overflow-y-scroll overscroll-contain">
                <div v-for="(mail, idx) in outgoingMails.data" @click="openMail(mail)"
                    class="flex flex-col space-y-1 cursor-pointer"
                    :class="{ 'bg-gray-200 rounded': mail.name == currentMail }">
                    <SidebarDetail :mail="mail" />
                    <div :class="{ 'mx-4 h-[0.25px] border-b border-gray-100': idx < outgoingMails.data.length - 1 }"></div>
                </div>
            </div>
            <div class="flex w-px cursor-col-resize justify-center" @mousedown="startResizing">
                <div ref="resizer"
                    class="h-full w-[2px] rounded-full transition-all duration-300 ease-in-out group-hover:bg-gray-400" />
            </div>
            <div class="flex-1 overflow-auto w-2/3">
                <MailDetails :mailID="currentMail" type="Outgoing Mail"/>
            </div>
        </div>
    </div>
</template>
<script setup>
import { Breadcrumbs, createResource, createListResource } from 'frappe-ui';
import { computed, inject, ref, onMounted } from 'vue';
import HeaderActions from "@/components/HeaderActions.vue";
import { formatNumber, startResizing, singularize } from "@/utils";
import MailDetails from "@/components/MailDetails.vue";
import { useDebounceFn } from '@vueuse/core'
import SidebarDetail from "@/components/SidebarDetail.vue";

const socket = inject('$socket')
const user = inject("$user");
const mailStart = ref(0)
const mailList = ref([])
const currentMail = ref(JSON.parse(sessionStorage.getItem("currentOutgoingMail")))

onMounted(() => {
    socket.on('outgoing_mail_sent', (data) => {
		outgoingMails.reload()
        outgoingMailCount.reload()
	})
})

const outgoingMails = createListResource({
    url: "mail.api.mail.get_outgoing_mails",
    doctype: "Outgoing Mail",
    auto: true,
    start: mailStart.value,
    pageLength: 50,
    cache: ["outgoing", user.data?.name],
    onSuccess(data) {
        mailList.value = mailList.value.concat(data)
        mailStart.value = mailStart.value + data.length
        if (!currentMail.value && mailList.value.length) {
            setCurrentMail(mailList.value[0].name)
        }
    }
});

const outgoingMailCount = createResource({
    url: "frappe.client.get_count",
    makeParams(values) {
        return {
            doctype: "Outgoing Mail",
            filters: {
                sender: user.data?.name,
                status: "Sent"
            }
        }
    },
    cache: ["outgoingMailCount", user.data?.name],
    auto: true,
})

const loadMoreEmails = useDebounceFn(() => {
    if (outgoingMails.hasNextPage)
        outgoingMails.next()
}, 500)

const setCurrentMail = (mail) => {
    sessionStorage.setItem("currentOutgoingMail", JSON.stringify(mail))
}

const openMail = (mail) => {
    currentMail.value = mail.name;
    setCurrentMail(mail.name)
}

const breadcrumbs = computed(() => {
    return [
        {
            label: "Sent",
            route: { name: "Sent" }
        }
    ];
});
</script>