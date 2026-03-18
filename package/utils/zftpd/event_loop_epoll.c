/*
 * event_loop_epoll.c — Linux epoll backend for the portable event loop.
 *
 * Copyright (c) 2026 Seregon — MIT License
 * Linux port contributed by REG-Linux.
 */

#include "event_loop.h"

#include <errno.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/epoll.h>

#define MAX_HANDLERS 1024
#define MAX_EVENTS   1024

/* ------------------------------------------------------------------ */
/*  Handler table (mirrors the kqueue backend)                        */
/* ------------------------------------------------------------------ */

typedef struct {
    int              fd;
    event_callback_t cb;
    void            *ctx;
} handler_entry_t;

struct event_loop {
    int                epfd;
    struct epoll_event events[MAX_EVENTS];
    handler_entry_t    handlers[MAX_HANDLERS];
    int                handler_count;
    atomic_bool        running;
};

/* singleton, same pattern as the kqueue backend */
static struct event_loop g_loop;

/* ------------------------------------------------------------------ */
/*  Lifetime                                                          */
/* ------------------------------------------------------------------ */

event_loop_t *event_loop_create(void)
{
    memset(&g_loop, 0, sizeof(g_loop));

    g_loop.epfd = epoll_create1(EPOLL_CLOEXEC);
    if (g_loop.epfd < 0)
        return NULL;

    g_loop.handler_count = 0;
    atomic_store(&g_loop.running, false);
    return &g_loop;
}

void event_loop_destroy(event_loop_t *loop)
{
    if (!loop) return;
    if (loop->epfd >= 0) {
        close(loop->epfd);
        loop->epfd = -1;
    }
    loop->handler_count = 0;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

static handler_entry_t *find_handler(event_loop_t *loop, int fd)
{
    for (int i = 0; i < loop->handler_count; i++) {
        if (loop->handlers[i].fd == fd)
            return &loop->handlers[i];
    }
    return NULL;
}

static uint32_t to_epoll_mask(uint32_t ev)
{
    uint32_t mask = 0;
    if (ev & EVENT_READ)  mask |= EPOLLIN;
    if (ev & EVENT_WRITE) mask |= EPOLLOUT;
    mask |= EPOLLRDHUP;          /* detect orderly peer shutdown */
    return mask;
}

static uint32_t from_epoll_mask(uint32_t ep)
{
    uint32_t mask = 0;
    if (ep & EPOLLIN)                  mask |= EVENT_READ;
    if (ep & EPOLLOUT)                 mask |= EVENT_WRITE;
    if (ep & (EPOLLHUP | EPOLLRDHUP))  mask |= EVENT_CLOSE;
    if (ep & EPOLLERR)                 mask |= EVENT_ERROR;
    return mask;
}

/* ------------------------------------------------------------------ */
/*  Registration                                                      */
/* ------------------------------------------------------------------ */

int event_loop_add(event_loop_t *loop, int fd, uint32_t events,
                   event_callback_t cb, void *ctx)
{
    if (!loop || fd < 0 || !cb)             return -1;
    if (loop->handler_count >= MAX_HANDLERS) return -1;

    handler_entry_t *h = find_handler(loop, fd);
    if (!h)
        h = &loop->handlers[loop->handler_count++];

    h->fd  = fd;
    h->cb  = cb;
    h->ctx = ctx;

    struct epoll_event ev = {
        .events  = to_epoll_mask(events),
        .data.fd = fd
    };
    return epoll_ctl(loop->epfd, EPOLL_CTL_ADD, fd, &ev);
}

int event_loop_modify(event_loop_t *loop, int fd, uint32_t events)
{
    if (!loop || fd < 0) return -1;

    struct epoll_event ev = {
        .events  = to_epoll_mask(events),
        .data.fd = fd
    };
    return epoll_ctl(loop->epfd, EPOLL_CTL_MOD, fd, &ev);
}

int event_loop_remove(event_loop_t *loop, int fd)
{
    if (!loop || fd < 0) return -1;

    (void)epoll_ctl(loop->epfd, EPOLL_CTL_DEL, fd, NULL);

    /* compact the handler table */
    for (int i = 0; i < loop->handler_count; i++) {
        if (loop->handlers[i].fd == fd) {
            loop->handlers[i] = loop->handlers[--loop->handler_count];
            break;
        }
    }
    return 0;
}

/* ------------------------------------------------------------------ */
/*  Main loop                                                         */
/* ------------------------------------------------------------------ */

int event_loop_run(event_loop_t *loop)
{
    if (!loop) return -1;

    atomic_store(&loop->running, true);

    while (atomic_load(&loop->running)) {
        int n = epoll_wait(loop->epfd, loop->events, MAX_EVENTS, 1000);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }

        for (int i = 0; i < n; i++) {
            int      fd = loop->events[i].data.fd;
            uint32_t ev = from_epoll_mask(loop->events[i].events);

            handler_entry_t *h = find_handler(loop, fd);
            if (!h) continue;

            int rc = h->cb(fd, ev, h->ctx);
            if (rc < 0)
                event_loop_remove(loop, fd);
        }
    }

    return 0;
}

void event_loop_stop(event_loop_t *loop)
{
    if (loop)
        atomic_store(&loop->running, false);
}
