export { addNotification, dismissNotification, mergeNotifications,autoDismissNotifications, myNotification, lNotifications }
const {ref} = Vue;


const successTimeLimit = 3000; // ms
const failureTimeLimit = 5000; // ms

const notificationTimeouts = {
  success: successTimeLimit,
  failure: failureTimeLimit,
};

class myNotification 
{
    constructor(id, content, kind, isSticky = false, {label = null, action = null } = {})
    {
        this.id = id;
        this.content = content;
        this.kind = kind;
        this.isSticky = isSticky;
        this.timeout = isSticky ? null : (notificationTimeouts[kind] ?? null);
        this.remainingSeconds = this.timeout === null
            ? null
            : Math.ceil(this.timeout / 1000);
        this.label = label;
        this.action = action;
    }
}

const notificationCountLimit = 5;
const lNotifications = ref([]);
const notificationTimers = new Map();

function addNotification(pNotification) 
{
    if (lNotifications.value.length >= notificationCountLimit) {
        if (lNotifications.value[0].isSticky) 
        {
            // If the first notification is sticky, we cannot dismiss it automatically.
            dismissNotification(lNotifications.value[1].id);
        }
        else
            dismissNotification(lNotifications.value[0].id);
    }
    lNotifications.value.push(pNotification);
    mergeNotifications();
    autoDismissNotifications(pNotification);
}

function dismissNotification(pId)
{
    const timer = notificationTimers.get(pId);
    if (timer) {
        clearTimeout(timer.timeoutId);
        clearInterval(timer.intervalId);
        notificationTimers.delete(pId);
    }
    lNotifications.value = lNotifications.value.filter((n) => n.id !== pId);
} 

function mergeNotifications()
{
    for (const newNotification of lNotifications.value)
    {
        const mergeCond = (n) => n.content === newNotification.content && n.kind === newNotification.kind;
        const existingNotification = lNotifications.value.find(mergeCond);
        if (existingNotification && existingNotification.id !== newNotification.id)
        {
            // Merge the notifications by keeping the new one and removing the existing one
            dismissNotification(existingNotification.id);
        }
    }
}

function autoDismissNotifications(notification)
{
    if (notification.timeout === null) return;

    const expiresAt = Date.now() + notification.timeout;
    const intervalId = setInterval(() => {
        const currentNotification = lNotifications.value.find(
            (item) => item.id === notification.id
        );
        if (currentNotification) {
            currentNotification.remainingSeconds = Math.max(
                0,
                Math.ceil((expiresAt - Date.now()) / 1000)
            );
        }
    }, 100);
    const timeoutId = setTimeout(() => {
        dismissNotification(notification.id);
    }, notification.timeout);
    notificationTimers.set(notification.id, { timeoutId, intervalId });
}